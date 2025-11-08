from typing import Any, Generator, ClassVar, Literal

import logging
import math
import platform
import sys
from uuid import UUID

import httpx
from urllib.parse import urljoin
from tenacity import Retrying, TryAgain, RetryCallState, retry_if_exception_type
from tenacity.wait import wait_exponential
from tenacity.stop import stop_after_attempt


import blockbax_sdk as bx
from . import api_utils


log = logging.getLogger(__name__)


class BlockbaxAuth(httpx.Auth):
    def __init__(self, token: str):
        self.token = token

    # Override
    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"ApiKey {self.token}"
        yield request


BASE_URL = "https://api.blockbax.com"
DEFAULT_API_VERSION = "v1"
PROJECTS_ENDPOINT = "projects"


def get_base_project_url(
    project_id: str | UUID,
    base_url: str = BASE_URL,
    api_version: str = DEFAULT_API_VERSION,
    projects_endpoint: str = PROJECTS_ENDPOINT,
) -> str:
    """
    Constructs the complete URL for accessing a specific project in the Blockbax API.
    This approach also handles trailing slashes in the endpoint args.
    Args:
        project_id (str|UUID): The unique identifier for the project.
        base_url (str, optional): The base URL of the API. Defaults to BASE_URL, which is "https://api.blockbax.com".
        api_version (str, optional): The API version to be used. Defaults to DEFAULT_API_VERSION, which is "v1".
        projects_endpoint (str, optional): The endpoint for projects in the API. Defaults to PROJECTS_ENDPOINT, which is "projects".

    Returns:
        str: The complete URL for the specified project in the Blockbax API.
    """
    if isinstance(project_id, UUID):
        project_id = str(project_id)

    # Ensure no leading slashes and consistent structure
    base_url = base_url.rstrip("/") + "/"
    api_version = api_version.strip("/") + "/"
    projects_endpoint = projects_endpoint.strip("/") + "/"

    return urljoin(
        urljoin(urljoin(base_url, api_version), projects_endpoint), project_id
    )


class BlockbaxHTTPSession(httpx.Client):
    user_agent: ClassVar[str] = (
        f"Blockbax Python SDK/{bx.__version__} HTTPX/{httpx.__version__} Python/{sys.version} {platform.platform()}".replace(
            "\n", ""
        )
    )
    tries: ClassVar[int] = 3
    back_off_factor: ClassVar[int] = 1
    status_force_list: ClassVar[list[int]] = [
        httpx.codes.BAD_GATEWAY,
        httpx.codes.SERVICE_UNAVAILABLE,
        httpx.codes.GATEWAY_TIMEOUT,
    ]
    timeout_seconds: ClassVar[float] = 10.0
    _sleep_buffer: ClassVar[int] = 1

    retryer: Retrying
    rate_limit_option: api_utils.RateLimitOption

    def __init__(
        self,
        token: str,
        project_id: str,
        endpoint: str,
        rate_limit_option: api_utils.RateLimitOption = api_utils.RateLimitOption.SLEEP,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.rate_limit_option = rate_limit_option
        self.retryer = Retrying(
            # Reraise the original error after the last attempt failed
            reraise=True,
            # Retry only if TryAgain is raised, e.g., for status_force_list codes
            retry=retry_if_exception_type(TryAgain),
            # Return the result of the last call attempt
            retry_error_callback=self.__retry_error_callback,
            # Exponential backoff
            wait=wait_exponential(multiplier=self.back_off_factor, min=1, max=10),
            # Stop retrying after the defined number of tries
            stop=stop_after_attempt(self.tries),
        )
        headers = httpx.Headers(
            {
                "Content-Type": "application/json",
                "User-Agent": self.user_agent,
            }
        )

        super(BlockbaxHTTPSession, self).__init__(
            trust_env=False,
            event_hooks={
                "request": [self.request_hook],
                "response": [self.response_hook],
            },
            headers=headers,
            auth=BlockbaxAuth(token),
            base_url=httpx.URL(
                get_base_project_url(base_url=endpoint, project_id=project_id)
            ),
            timeout=httpx.Timeout(self.timeout_seconds),
            *args,
            **kwargs,
        )

    # Overwrite
    def request(self, *args: Any, **kwargs: Any) -> httpx.Response:
        try:
            return self.retryer(
                super(BlockbaxHTTPSession, self).request, *args, **kwargs
            )

        except TryAgain as exc:
            # Internally raised by the rate limit handler
            # If for some reason this fails after the amount of tries 'TryAgain' would be re-raised.
            raise RuntimeError(
                f"Unexpected error, retrying requests due to rate limiter failed after {self.tries} tries."
            ) from exc

    def __retry_error_callback(self, retry_state: RetryCallState) -> httpx.Response:
        retry_outcome = retry_state.outcome
        if retry_outcome is not None:
            return retry_outcome.result()
        raise RuntimeError(
            "Unexpected error, retry failed but the last outcome is 'None'. Expecting at least one "
            "outcome with a response."
        )

    def request_hook(self, request: httpx.Request):
        """Request hook is called right before the request is made"""

    def response_hook(self, response: httpx.Response):
        """Response hook is called right after a request has been made"""

        # Immediately raise error if the access token is not unauthorized
        api_utils.raise_for_unauthorized_error(response)

        # Force a retry if the status code is in the 'status_force_list'
        if response.status_code in self.status_force_list:
            raise TryAgain(response.text)

        # Handle rate limits retries
        api_utils.handle_rate_limiter(
            response, self.rate_limit_option, self._sleep_buffer
        )
        # Handles different HTTP error cases, either log errors or raises new Blockbax Errors
        client_error_codes = (
            [400, 402, 403] + list(range(405, 429)) + list(range(430, 500))
        )

        api_utils.raise_client_error(response, client_error_codes)
        server_error_codes = list(range(500, 600))
        api_utils.raise_server_error(response, server_error_codes)

        # Handles HTTP status codes that are not an error or not found
        api_utils.notify_partial_accepted(response)
        api_utils.notify_not_found(response)


class Api:
    # settings
    access_token: str
    project_id: str
    default_page_size: int = 200
    # endpoints
    property_types_endpoint: str = "propertyTypes"
    subject_types_endpoint: str = "subjectTypes"
    subjects_endpoint: str = "subjects"
    metrics_endpoint: str = "metrics"
    measurements_endpoint: str = "measurements"
    event_triggers_endpoint = "eventTriggers"
    events_endpoint = "events"

    def __init__(self, access_token: str, project_id: str, endpoint: str | None = None):
        """Initialize the API client.

        Args:
            access_token (str): The secret access token for authentication.
            project_id (str): The Blockbax projectID.
            endpoint (str | None, optional): The base API endpoint URL. Defaults to None.
        """
        self.access_token = access_token
        self.project_id = project_id
        self.endpoint = endpoint or BASE_URL

    def session(self) -> BlockbaxHTTPSession:
        """Create and return a new HTTP session.

        Returns:
            BlockbaxHTTPSession: A configured HTTP session instance.
        """
        return BlockbaxHTTPSession(self.access_token, self.project_id, self.endpoint)

    def get_user_agent(self) -> str:
        """Get the user agent string for HTTP requests.

        Returns:
            str: The user agent string.
        """
        return BlockbaxHTTPSession.user_agent

    # http requests
    def get(
        self,
        endpoint: str = "",
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Get a single entry from the API using ID.

        Args:
            endpoint (str, optional): The API endpoint to request. Defaults to "".
            params (dict[str, Any] | None, optional): Query parameters for the request. Defaults to None.

        Returns:
            dict[str, Any] | None: The response data or None if the request fails.
        """
        if params is None:
            params = {}
        params = {k: v for k, v in params.items() if v is not None}
        with self.session() as session:
            return api_utils.parse_response(session.get(url=endpoint, params=params))  # type: ignore

    def search(
        self, endpoint: str = "", params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Search multiple entries from the API using automatic paging.

        Args:
            endpoint (str, optional): The API endpoint to search. Defaults to "".
            params (dict[str, Any] | None, optional): Query parameters for the search. Defaults to None.

        Returns:
            list[dict[str, Any]]: A list of results from all pages.
        """

        if not params:
            params = {}
        params = {k: v for k, v in params.items() if v is not None}
        params["size"] = self.default_page_size

        current_page_index = 0
        last_page_number = None
        results: list[dict[str, Any]] = []
        done = False
        # while the previous page is not equal to the last page index get the current page index

        with self.session() as session:
            while not done:
                params["page"] = current_page_index
                response = api_utils.parse_response(
                    session.get(url=endpoint, params=params)
                )
                if response is None:
                    return results
                result = response.get("result")
                results.extend(result if result is not None else [])
                if response.get("count") is None:
                    return results  # return because we do not know when to stop

                if last_page_number is None:
                    last_page_number = math.ceil(
                        response["count"] / params["size"]
                    )  # page index starts from 0
                current_page_index += 1

                if current_page_index >= last_page_number:
                    done = True
        return results

    def post(self, endpoint: str, json: dict[str, Any]) -> dict[str, Any] | None:
        """Create a new resource via POST request.

        Args:
            endpoint (str): The API endpoint to post to.
            json (dict[str, Any]): The JSON payload for the request.

        Returns:
            dict[str, Any] | None: The response data or None if the request fails.
        """
        with self.session() as session:
            return api_utils.parse_response(  # type: ignore
                session.post(
                    url=endpoint,
                    json=json,
                )
            )

    def put(self, endpoint: str, json: dict[str, Any]) -> dict[str, Any] | None:
        """Update an existing resource via PUT request.

        Args:
            endpoint (str): The API endpoint to update.
            json (dict[str, Any]): The JSON payload for the request.

        Returns:
            dict[str, Any] | None: The response data or None if the request fails.
        """
        with self.session() as session:
            return api_utils.parse_response(  # type: ignore
                session.put(
                    url=endpoint,
                    json=json,
                )
            )

    def delete(self, endpoint: str):
        """Delete a resource via DELETE request.

        Args:
            endpoint (str): The API endpoint to delete.
        """
        with self.session() as session:
            session.delete(endpoint)

    # project

    def get_project(self) -> dict[str, Any] | None:
        """Get the current project information.

        Returns:
            dict[str, Any] | None: The project data or None if not found.
        """
        project_root_full_url = get_base_project_url(
            project_id=self.project_id, base_url=self.endpoint
        )
        return self.get(endpoint=project_root_full_url)

    # property types

    def get_property_type(self, property_type_id: str) -> dict[str, Any] | None:
        """Get a single property type by ID.

        Args:
            property_type_id (str): The ID of the property type.

        Returns:
            dict[str, Any] | None: The property type data or None if not found.
        """
        return self.get(endpoint=f"{self.property_types_endpoint}/{property_type_id}")

    def get_property_types(
        self, name: str | None = None, external_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Search for property types by name or external ID.

        Args:
            name (str | None, optional): The name to filter by. Defaults to None.
            external_id (str | None, optional): The external ID to filter by. Defaults to None.

        Returns:
            list[dict[str, Any]]: A list of property types matching the criteria.
        """
        params = {"name": name, "externalId": external_id}
        return self.search(self.property_types_endpoint, params=params)

    def create_property_type(
        self,
        name: str,
        external_id: str,
        data_type: str,
        predefined_values: bool = False,
        values: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        """Create a new property type.

        Args:
            name (str): The name of the property type.
            external_id (str): The external ID for the property type.
            data_type (str): The data type of the property.
            predefined_values (bool, optional): Whether the property has predefined values. Defaults to False.
            values (list[dict[str, Any]] | None, optional): The list of predefined values. Defaults to None.

        Returns:
            dict[str, Any] | None: The created property type data or None if creation fails.
        """
        body = {
            "name": name,
            "externalId": external_id,
            "dataType": data_type,
            "predefinedValues": predefined_values,
            "values": values,
        }
        response = self.post(endpoint=self.property_types_endpoint, json=body)
        return response

    def update_property_type(
        self, property_type_id: str, json: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update an existing property type.

        Args:
            property_type_id (str): The ID of the property type to update.
            json (dict[str, Any]): The JSON payload with updated fields.

        Returns:
            dict[str, Any] | None: The updated property type data or None if update fails.
        """
        response = self.put(
            endpoint=f"{self.property_types_endpoint}/{property_type_id}", json=json
        )
        return response

    def delete_property_type(self, property_type_id: str):
        """Delete a property type by ID.

        Args:
            property_type_id (str): The ID of the property type to delete.
        """
        self.delete(endpoint=f"{self.property_types_endpoint}/{property_type_id}")

    # subject types

    def get_subject_type(self, subject_type_id: str) -> dict[str, Any] | None:
        """Get a single subject type by ID.

        Args:
            subject_type_id (str): The ID of the subject type.

        Returns:
            dict[str, Any] | None: The subject type data or None if not found.
        """
        return self.get(endpoint=f"{self.subject_types_endpoint}/{subject_type_id}")

    def get_subject_types(
        self,
        name: str | None = None,
        property_type_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for subject types by name or property type IDs.

        Args:
            name (str | None, optional): The name to filter by. Defaults to None.
            property_type_ids (list[str] | None, optional): The list of property type IDs to filter by. Defaults to None.

        Returns:
            list[dict[str, Any]]: A list of subject types matching the criteria.
        """
        params = {"name": name, "propertyTypes": property_type_ids}
        return self.search(endpoint=f"{self.subject_types_endpoint}", params=params)

    def create_subject_type(
        self,
        name: str,
        parent_subject_type_ids: list[str] | None = None,
        primary_location: dict[str, Any] | None = None,
        property_types: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        """Create a new subject type.

        Args:
            name (str): The name of the subject type.
            parent_subject_type_ids (list[str] | None, optional): The list of parent subject type IDs. Defaults to None.
            primary_location (dict[str, Any] | None, optional): The primary location configuration. Defaults to None.
            property_types (list[dict[str, Any]] | None, optional): The list of property types for this subject type. Defaults to None.

        Returns:
            dict[str, Any] | None: The created subject type data or None if creation fails.
        """
        body = {
            "name": name,
            "parentSubjectTypeIds": parent_subject_type_ids,
            "primaryLocation": primary_location,
            "propertyTypes": property_types,
        }
        response = self.post(endpoint=self.subject_types_endpoint, json=body)
        return response

    def update_subject_type(
        self,
        subject_type_id: str,
        json: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Update an existing subject type.

        Args:
            subject_type_id (str): The ID of the subject type to update.
            json (dict[str, Any]): The JSON payload with updated fields.

        Returns:
            dict[str, Any] | None: The updated subject type data or None if update fails.
        """
        return self.put(
            endpoint=f"{self.subject_types_endpoint}/{subject_type_id}", json=json
        )

    def delete_subject_type(self, subject_type_id: str):
        """Delete a subject type by ID.

        Args:
            subject_type_id (str): The ID of the subject type to delete.
        """
        self.delete(endpoint=f"{self.subject_types_endpoint}/{subject_type_id}")

    # subjects

    def get_subject(self, subject_id: str) -> dict[str, Any] | None:
        """Get a single subject by ID.

        Args:
            subject_id (str): The ID of the subject.

        Returns:
            dict[str, Any] | None: The subject data or None if not found.
        """
        return self.get(endpoint=f"{self.subjects_endpoint}/{subject_id}")

    def get_subjects(
        self,
        name: str | None = None,
        subject_ids: list[str] | None = None,
        subject_type_ids: list[Any] | None = None,
        subject_ids_mode: str | None = None,
        subject_external_id: str | None = None,
        property_value_ids: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for subjects by various criteria.

        Args:
            name (str | None, optional): The name to filter by. Defaults to None.
            subject_ids (list[str] | None, optional): The list of subject IDs to filter by. Defaults to None.
            subject_type_ids (list[Any] | None, optional): The list of subject type IDs to filter by. Defaults to None.
            subject_ids_mode (str | None, optional): The mode for filtering by subject IDs. Defaults to None.
            subject_external_id (str | None, optional): The external ID to filter by. Defaults to None.
            property_value_ids (str | None, optional): The property value IDs to filter by. Defaults to None.

        Returns:
            list[dict[str, Any]]: A list of subjects matching the criteria.
        """
        return self.search(
            endpoint=self.subjects_endpoint,
            params={
                "name": name,
                "subjectIds": subject_ids,
                "subjectTypeIds": subject_type_ids,
                "subjectIdsMode": subject_ids_mode,
                "externalId": subject_external_id,
                "propertyValueIds": property_value_ids,
            },
        )

    def create_subject(
        self,
        name: str,
        subject_type_id: str,
        external_id: str,
        ingestion_ids: list[Any],
        parent_subject_id: str | None = None,
        properties: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any] | None:
        """Create a new subject.

        Args:
            name (str): The name of the subject.
            subject_type_id (str): The ID of the subject type.
            external_id (str): The external ID for the subject.
            ingestion_ids (list[Any]): The list of ingestion IDs.
            parent_subject_id (str | None, optional): The ID of the parent subject. Defaults to None.
            properties (list[dict[str, Any]] | None, optional): The list of properties for the subject. Defaults to None.

        Returns:
            dict[str, Any] | None: The created subject data or None if creation fails.
        """
        body = {
            "name": name,
            "subjectTypeId": subject_type_id,
            "parentSubjectId": parent_subject_id,
            "externalId": external_id,
            "ingestionIds": ingestion_ids,
            "properties": properties,
        }
        return self.post(endpoint=self.subjects_endpoint, json=body)

    def update_subject(
        self, subject_id: str, json: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update an existing subject.

        Args:
            subject_id (str): The ID of the subject to update.
            json (dict[str, Any]): The JSON payload with updated fields.

        Returns:
            dict[str, Any] | None: The updated subject data or None if update fails.
        """
        return self.put(
            endpoint=f"{self.subjects_endpoint}/{subject_id}",
            json=json,
        )

    def delete_subject(self, subject_id: str):
        """Delete a subject by ID.

        Args:
            subject_id (str): The ID of the subject to delete.
        """
        self.delete(endpoint=f"{self.subjects_endpoint}/{subject_id}")

    # metrics

    def get_metric(self, metric_id: str) -> dict[str, Any] | None:
        """Get a single metric by ID.

        Args:
            metric_id (str): The ID of the metric.

        Returns:
            dict[str, Any] | None: The metric data or None if not found.
        """
        return self.get(endpoint=f"{self.metrics_endpoint}/{metric_id}")

    def get_metrics(
        self,
        name: str | None = None,
        subject_type_ids: list[str] | None = None,
        metric_external_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for metrics by name, subject type IDs, or external ID.

        Args:
            name (str | None, optional): The name to filter by. Defaults to None.
            subject_type_ids (list[str] | None, optional): The list of subject type IDs to filter by. Defaults to None.
            metric_external_id (str | None, optional): The external ID to filter by. Defaults to None.

        Returns:
            list[dict[str, Any]]: A list of metrics matching the criteria.
        """
        params = {
            "name": name,
            "subjectTypeIds": subject_type_ids,
            "externalId": metric_external_id,
        }
        return self.search(endpoint=self.metrics_endpoint, params=params)

    def create_metric(
        self,
        subject_type_id: str,
        name: str,
        data_type: str,
        type_: str,
        external_id: str,
        mapping_level: str,
        unit: str | None = None,
        precision: int | None = None,
        visible: bool | None = None,
        discrete: bool | None = None,
        preferred_color: str | None = None,
    ) -> dict[str, Any] | None:
        """Create a new metric.

        Args:
            subject_type_id (str): The ID of the subject type.
            name (str): The name of the metric.
            data_type (str): The data type of the metric.
            type_ (str): The type of the metric.
            external_id (str): The external ID for the metric.
            mapping_level (str): The mapping level of the metric.
            unit (str | None, optional): The unit of measurement. Defaults to None.
            precision (int | None, optional): The precision of the metric values. Defaults to None.
            visible (bool | None, optional): Whether the metric is visible. Defaults to None.
            discrete (bool | None, optional): Whether the metric is discrete. Defaults to None.
            preferred_color (str | None, optional): The preferred color for visualization. Defaults to None.

        Returns:
            dict[str, Any] | None: The created metric data or None if creation fails.
        """
        body = {
            "name": name,
            "externalId": external_id,
            "subjectTypeId": subject_type_id,
            "dataType": data_type,
            "unit": unit,
            "preferredColor": preferred_color,
            "precision": precision,
            "visible": visible,
            "type": type_,
            "discrete": discrete,
            "mappingLevel": mapping_level,
        }
        response = self.post(endpoint=self.metrics_endpoint, json=body)
        return response

    def update_metric(
        self,
        metric_id: str,
        json: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Update an existing metric.

        Args:
            metric_id (str): The ID of the metric to update.
            json (dict[str, Any]): The JSON payload with updated fields.

        Returns:
            dict[str, Any] | None: The updated metric data or None if update fails.
        """
        return self.put(endpoint=f"{self.metrics_endpoint}/{metric_id}", json=json)

    def delete_metric(self, metric_id: str):
        """Delete a metric by ID.

        Args:
            metric_id (str): The ID of the metric to delete.
        """
        self.delete(endpoint=f"{self.metrics_endpoint}/{metric_id}")

    # measurements

    def get_measurements(
        self,
        subject_ids: list[str] | None = None,
        metric_ids: list[str] | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        size: int | None = None,
        order: str | None = None,
    ) -> dict[str, Any] | None:
        """Get measurements based on various criteria.

        Args:
            subject_ids (list[str] | None, optional): The list of subject IDs to filter by. Defaults to None.
            metric_ids (list[str] | None, optional): The list of metric IDs to filter by. Defaults to None.
            from_date (str | None, optional): The start date for filtering (inclusive). Defaults to None.
            to_date (str | None, optional): The end date for filtering (exclusive). Defaults to None.
            size (int | None, optional): The maximum number of measurements to return. Defaults to None.
            order (str | None, optional): The sort order for results. Defaults to None.

        Returns:
            dict[str, Any] | None: The measurements data or None if not found.
        """
        params = {
            "subjectIds": ",".join(subject_ids) if subject_ids is not None else None,
            "metricIds": ",".join(metric_ids) if metric_ids is not None else None,
            "fromDate": from_date,
            "toDate": to_date,
            "size": size,
            "order": order,
        }
        return self.get(endpoint=self.measurements_endpoint, params=params)

    def send_measurements(self, series: dict[str, Any]) -> dict[str, Any] | None:
        """Send measurement data to the API.

        Args:
            series (dict[str, Any]): The measurement series data to send.

        Returns:
            dict[str, Any] | None: The response data or None if the request fails.
        """
        response = self.post(endpoint=self.measurements_endpoint, json=series)
        return response

    ## event triggers

    def get_event_trigger(self, event_trigger_id: str) -> dict[str, Any] | None:
        """Get a single event trigger by ID.

        Args:
            event_trigger_id (str): The ID of the event trigger.

        Returns:
            dict[str, Any] | None: The event trigger data or None if not found.
        """
        return self.get(endpoint=f"{self.event_triggers_endpoint}/{event_trigger_id}")

    def get_event_triggers(
        self,
        name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for event triggers by name.

        Args:
            name (str | None, optional): The name to filter by. Defaults to None.

        Returns:
            list[dict[str, Any]]: A list of event triggers matching the criteria.
        """
        params = {
            "name": name,
        }
        return self.search(endpoint=self.event_triggers_endpoint, params=params)

    def create_event_trigger(
        self,
        name: str,
        subject_type_id: str,
        active: bool,
        evaluation_trigger: Literal["INPUT_METRICS", "SUBJECT_METRICS"],
        evaluation_constraint: Literal["NONE", "ALL_TIMESTAMPS_MATCH"],
        event_rules: list[dict[str, Any]],
        subject_filter: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Create a new event trigger.

        Args:
            name (str): The name of the event trigger.
            subject_type_id (str): The ID of the subject type.
            active (bool): Whether the event trigger is active.
            evaluation_trigger (Literal["INPUT_METRICS", "SUBJECT_METRICS"]): The evaluation trigger type.
            evaluation_constraint (Literal["NONE", "ALL_TIMESTAMPS_MATCH"]): The evaluation constraint type.
            event_rules (list[dict[str, Any]]): The list of event rules.
            subject_filter (dict[str, Any] | None, optional): The subject filter configuration. Defaults to None.

        Returns:
            dict[str, Any] | None: The created event trigger data or None if creation fails.
        """
        body = {
            "name": name,
            "subjectTypeId": subject_type_id,
            "active": active,
            "evaluationTrigger": evaluation_trigger,
            "evaluationConstraint": evaluation_constraint,
            "eventRules": event_rules,
            "subjectFilter": subject_filter,
        }
        return self.post(endpoint=self.event_triggers_endpoint, json=body)

    def update_event_trigger(
        self, event_trigger_id: str, json: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Update an existing event trigger.

        Args:
            event_trigger_id (str): The ID of the event trigger to update.
            json (dict[str, Any]): The JSON payload with updated fields.

        Returns:
            dict[str, Any] | None: The updated event trigger data or None if update fails.
        """
        return self.put(
            endpoint=f"{self.event_triggers_endpoint}/{event_trigger_id}", json=json
        )

    def delete_event_trigger(self, event_trigger_id: str):
        """Delete an event trigger by ID.

        Args:
            event_trigger_id (str): The ID of the event trigger to delete.
        """
        self.delete(endpoint=f"{self.event_triggers_endpoint}/{event_trigger_id}")

    # Events:
    def get_event(self, event_id: str) -> dict[str, Any] | None:
        """Retrieve a single event by its ID.

        Args:
            event_id (str): The ID of the event.

        Returns:
            dict[str, Any] | None: The event data if found, else None.
        """
        return self.get(endpoint=f"{self.events_endpoint}/{event_id}")

    def get_events(
        self,
        active: bool | None = None,
        suppressed: bool | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        only_new: bool | None = None,
        property_value_ids: str | None = None,
        subject_ids: str | None = None,
        event_trigger_ids: str | None = None,
        event_levels: str | None = None,
        sort: str | None = "startDate,desc",
    ) -> list[dict[str, Any]]:
        """Get events based on various criteria.

        Args:
            active (bool | None, optional): True to fetch only active events. Defaults to None.
            suppressed (bool | None, optional): True to only fetch events that are suppressed, False to only fetch events that are not suppressed. Defaults to None.
            from_date (str | None, optional): Inclusive from date as ISO 8601 string with millisecond precision. Defaults to None.
            to_date (str | None, optional): Exclusive end date as ISO 8601 string with millisecond precision. Defaults to None.
            only_new (bool | None, optional): True to fetch only events occurred in the given date range. Defaults to None.
            property_value_ids (str | None, optional): Filter on a list of property value IDs. Defaults to None.
            subject_ids (str | None, optional): Comma-separated list of subject IDs. Defaults to None.
            event_trigger_ids (str | None, optional): Comma-separated list of event trigger IDs. Defaults to None.
            event_levels (str | None, optional): Comma-separated list of event levels. Defaults to None.
            sort (str | None, optional): The sort order. Defaults to "startDate,desc".

        Returns:
            list[dict[str, Any]]: A list of events matching the criteria.
        """
        params = {
            "active": active,
            "suppressed": suppressed,
            "fromDate": from_date,
            "toDate": to_date,
            "onlyNew": only_new,
            "propertyValueIds": property_value_ids,
            "subjectIds": subject_ids,
            "eventTriggerIds": event_trigger_ids,
            "eventLevels": event_levels,
            "sort": sort,
        }
        return self.search(endpoint=self.events_endpoint, params=params)
