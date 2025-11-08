from pathlib import Path
import time
from typing import Any, Literal, Sequence
from uuid import UUID
from decimal import Decimal
from ..util import deprecated

from ..models.metric import Metric
from ..models.ingestion import Ingestion
from ..models.property_type import PropertyType
from ..models.property_type_value import PropertyTypeValue
from ..models.subject_type import (
    SubjectType,
    SubjectTypePrimaryLocation,
    SubjectTypePropertyType,
)
from ..models.project import Project, ProjectResources
from ..models.measurement import measurement_adapter
from ..models.property_type_value import property_type_value_adapter
from ..models.ingestion import IngestionIdOverride
from ..models.subject_property import subject_property_adapter
from ..models.subject_property import SubjectProperty
from ..models.subject import Subject
from ..models.series import Series

from ..models.data_types import Location
from ..models.event_trigger import (
    EventTrigger,
    EventRule,
    SubjectFilter,
)
from ..models.event import Event
from ..util import conversions
from ..util import ingestion_queuer
from .api import api as bx_api

from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class HttpClient:
    """Client for interacting with the Blockbax API via HTTP requests.

    Provides high-level methods to interact with project resources such as property types,
    subject types, metrics, subjects, measurements, and events.
    """

    api: bx_api.Api
    project_id: str | None
    project: Project | None
    endpoint: str | None

    def __init__(self, access_token: str, project_id: str, endpoint: str | None = None):
        """Initialize the HTTP client.

        Args:
            access_token (str): The secret access token for API authentication.
            project_id (str): The Blockbax project ID.
            endpoint (str | None, optional): Custom API endpoint. Defaults to None.

        Raises:
            ValueError: If access_token or project_id is missing.
        """
        if access_token and project_id:
            self.project_id = project_id
            self.api = bx_api.Api(
                access_token=access_token, project_id=project_id, endpoint=endpoint
            )
        else:
            raise ValueError("Please provide both project ID and Access token!")
        self.ingestion_queuer = ingestion_queuer.IngestionQueuer()

    def load_project(self, directory_path: str | Path) -> ProjectResources:
        """Load project resources from a local directory (experimental).

        This helper method loads project-related resources from a specified directory.
        Note that this method is experimental and may be removed in a future release.

        Args:
            directory_path (str | Path): The path to the local project directory.

        Returns:
            ProjectResources: A container object with loaded project resources.

        Raises:
            ValueError: If the provided path is not a directory.
            RuntimeError: If no project details are found.
        """
        deprecated.deprecation_warning(
            "The 'load_project' method is experimental and will be removed in future releases."
        )
        directory_path = Path(directory_path)
        if directory_path.exists() and not directory_path.is_dir():
            raise ValueError(f"{directory_path} is not a directory")

        self.project = self.get_project_details()
        if self.project is None:
            raise RuntimeError("No project found")
        resources = ProjectResources(
            project=self.project,
            subjects=self.get_subjects(),
            metrics=self.get_metrics(),
            subject_types=self.get_subject_types(),
            property_types=self.get_property_types(),
        )

        return resources

    def get_user_agent(self) -> str:
        """Retrieve the user agent string used by this client.

        Returns:
            str: The user agent string including SDK, HTTP library, and Python version details.
        """
        return self.api.get_user_agent()  # type: ignore

    def get_project_details(self) -> Project | None:
        """Retrieve details of the current project.

        Returns:
            Project | None: The project details if found, else None.
        """
        project_api_response = self.api.get_project()
        return Project.from_response(project_api_response)

    def get_property_types(
        self,
        name: str | None = None,
        external_id: str | None = None,
    ) -> list[PropertyType]:
        """Retrieve property types with optional filters.

        Args:
            name (str | None, optional): Filter property types by name. Defaults to None.
            external_id (str | None, optional): Filter property types by external ID. Defaults to None.

        Returns:
            list[PropertyType]: The list of matching property types.
        """
        property_type_responses = self.api.get_property_types(
            name=name,
            external_id=external_id,
        )
        property_types = [
            PropertyType.from_response(property_type_response)
            for property_type_response in property_type_responses
        ]
        return [p for p in property_types if p is not None]

    def get_property_type(self, id_: UUID | str) -> PropertyType | None:
        """Retrieve a specific property type by its ID.

        Args:
            id_ (UUID | str): The property type ID.

        Returns:
            PropertyType | None: The property type if found, else None.
        """
        property_type_response = self.api.get_property_type(property_type_id=str(id_))
        return PropertyType.from_response(property_type_response)

    def create_property_type(
        self,
        name: str,
        external_id: str,
        data_type: Literal["NUMBER", "TEXT", "LOCATION", "MAP_LAYER", "IMAGE", "AREA"],
        predefined_values: bool,
        values: Sequence[dict[str, Any] | PropertyTypeValue] | None = None,
    ) -> PropertyType | None:
        """Create a new property type.

        Args:
            name (str): The property type name.
            external_id (str): The external identifier for the property type.
            data_type (Literal): The data type of the property type.
            predefined_values (bool): Whether predefined values are allowed.
            values (Sequence[dict[str, Any] | PropertyTypeValue] | None, optional): The predefined values, if any.

        Returns:
            PropertyType | None: The created property type if successful.

        Raises:
            ValueError: If values are provided while predefined_values is False.
        """
        if not predefined_values and values:
            raise ValueError(
                "Values can only be added to a property type with predefined values"
            )
        formatted_values = (
            [
                property_type_value_adapter.validate_python(v).to_request()
                for v in values
            ]
            if values is not None
            else None
        )

        property_type_response = self.api.create_property_type(
            name=name,
            external_id=external_id,
            data_type=data_type,
            predefined_values=predefined_values,
            values=formatted_values,
        )
        return PropertyType.from_response(property_type_response)

    def update_property_type(
        self,
        property_type: dict | PropertyType,
    ) -> PropertyType | None:
        """Update an existing property type.

        Args:
            property_type (dict | PropertyType): The property type object or dictionary to update.

        Returns:
            PropertyType | None: The updated property type if successful.
        """
        if isinstance(property_type, dict):
            property_type = PropertyType(**property_type)
        property_type_response = self.api.update_property_type(
            property_type_id=str(property_type.id),
            json=property_type.to_request(),
        )
        return PropertyType.from_response(property_type_response)

    def delete_property_type(self, id_: str | UUID):
        """Delete a property type by ID.

        Args:
            id_ (str | UUID): The property type ID.
        """
        self.api.delete_property_type(property_type_id=str(id_))

    def get_subject_types(
        self,
        name: str | None = None,
        property_type_ids: Sequence[str | UUID] | None = None,
    ) -> list[SubjectType]:
        """Retrieve subject types with optional filters.

        Args:
            name (str | None, optional): Filter subject types by name. Defaults to None.
            property_type_ids (Sequence[str | UUID] | None, optional): Filter by property type IDs. Defaults to None.

        Returns:
            list[SubjectType]: The list of matching subject types.
        """
        subject_type_responses = self.api.get_subject_types(
            name=name,
            property_type_ids=conversions.ensure_str_ids(property_type_ids),
        )
        subject_types = [
            SubjectType.from_response(subject_type_response)
            for subject_type_response in subject_type_responses
        ]
        return [st for st in subject_types if st is not None]

    def get_subject_type(self, id_: str | UUID) -> SubjectType | None:
        """Retrieve a specific subject type by ID.

        Args:
            id_ (str | UUID): The subject type ID.

        Returns:
            SubjectType | None: The subject type if found, else None.
        """
        subject_type_response = self.api.get_subject_type(subject_type_id=str(id_))
        if subject_type_response is None:
            return None
        return SubjectType.from_response(subject_type_response)

    def create_subject_type(
        self,
        name: str,
        parent_subject_type_ids: Sequence[str | UUID] | None = None,
        primary_location: SubjectTypePrimaryLocation | dict[str, Any] | None = None,
        property_types: (
            Sequence[SubjectTypePropertyType | dict[str, Any]] | None
        ) = None,
    ) -> SubjectType | None:
        """Create a new subject type.

        Args:
            name (str): The subject type name.
            parent_subject_type_ids (Sequence[str | UUID] | None, optional): The parent subject type IDs. Defaults to None.
            primary_location (SubjectTypePrimaryLocation | dict[str, Any] | None, optional): The primary location configuration. Defaults to None.
            property_types (Sequence[SubjectTypePropertyType | dict[str, Any]] | None, optional): Property types for this subject type. Defaults to None.

        Returns:
            SubjectType | None: The created subject type if successful.
        """
        validated_property_types: list[SubjectTypePropertyType] = []

        if property_types is not None:
            for p in property_types:
                validated_property_types.append(
                    SubjectTypePropertyType.model_validate(p)
                )

        validated_primary_location = None
        if primary_location is not None:
            if isinstance(primary_location, dict):
                validated_primary_location = SubjectTypePrimaryLocation(
                    **primary_location
                )
            elif isinstance(primary_location, SubjectTypePrimaryLocation):
                validated_primary_location = primary_location
            else:
                raise TypeError("Not a supported primary_location type")

            # Automatically add primary location property type to the list of property types
            if validated_primary_location.type == "PROPERTY_TYPE":
                for validated_property_type in validated_property_types:
                    if validated_primary_location.id == validated_property_type.id:
                        break
                else:
                    validated_property_types.append(
                        SubjectTypePropertyType(
                            id=validated_primary_location.id,
                            required=True,
                        )
                    )

        subject_type_response = self.api.create_subject_type(
            name=name,
            parent_subject_type_ids=conversions.ensure_str_ids(parent_subject_type_ids),
            primary_location=(
                validated_primary_location.to_request()
                if validated_primary_location is not None
                else None
            ),
            property_types=(
                [p.to_request() for p in validated_property_types]
                if validated_property_types
                else None
            ),
        )

        return SubjectType.from_response(subject_type_response)

    def update_subject_type(
        self,
        subject_type: SubjectType,
    ) -> SubjectType | None:
        """Update an existing subject type.

        Args:
            subject_type (SubjectType): The updated subject type object.

        Returns:
            SubjectType | None: The updated subject type if successful.
        """
        subject_type_response = self.api.update_subject_type(
            subject_type_id=str(subject_type.id),
            json=subject_type.to_request(),
        )

        return SubjectType.from_response(subject_type_response)

    def delete_subject_type(self, id_: str | UUID):
        """Delete a subject type by ID.

        Args:
            id_ (str | UUID): The subject type ID.
        """
        self.api.delete_subject_type(subject_type_id=str(id_))

    def get_metrics(
        self,
        name: str | None = None,
        metric_external_id: str | None = None,
        subject_type_ids: Sequence[str | UUID] | None = None,
    ) -> list[Metric]:
        """Retrieve metrics with optional filters.

        Args:
            name (str | None, optional): Filter metrics by name. Defaults to None.
            metric_external_id (str | None, optional): Filter metrics by external ID. Defaults to None.
            subject_type_ids (Sequence[str | UUID] | None, optional): Filter metrics by subject type IDs. Defaults to None.

        Returns:
            list[Metric]: The list of matching metrics.
        """
        metric_responses = self.api.get_metrics(
            name=name,
            metric_external_id=metric_external_id,
            subject_type_ids=conversions.ensure_str_ids(subject_type_ids),
        )
        metrics = [
            Metric.from_response(metric_response)
            for metric_response in metric_responses
            if Metric.from_response(metric_response) is not None
        ]
        return [metric for metric in metrics if metric is not None]

    def get_metric(self, id_: str | UUID) -> Metric | None:
        """Retrieve a specific metric by ID.

        Args:
            id_ (str | UUID): The metric ID.

        Returns:
            Metric | None: The metric if found, else None.
        """
        metric_response = self.api.get_metric(metric_id=str(id_))

        return Metric.from_response(metric_response)

    def create_metric(
        self,
        subject_type_id: str | UUID,
        name: str,
        data_type: Literal["NUMBER", "TEXT", "LOCATION"],
        type_: Literal["INGESTED"],  # type: ignore
        mapping_level: Literal["OWN", "CHILD"],
        external_id: str | None = None,
        unit: str | None = None,
        precision: int | None = None,
        visible: bool | None = True,
        discrete: bool | None = False,
        preferred_color: str | None = None,
    ) -> Metric | None:
        """Create a new metric for a subject type.

        Args:
            subject_type_id (str | UUID): ID of the subject type this metric belongs to.
            name (str): Human-readable name for the metric.
            data_type (Literal): Data type of the metric. One of "NUMBER", "TEXT", "LOCATION".
            type_ (Literal): Metric type. Currently only "INGESTED" is supported.
            mapping_level (Literal): Mapping level for ingestion. One of "OWN" or "CHILD".
            external_id (str | None, optional): External identifier for the metric. If None, one will be derived from the name.
            unit (str | None, optional): Unit of measurement for the metric.
            precision (int | None, optional): Display precision for numeric metrics (0-8).
            visible (bool | None, optional): Whether the metric is visible in the UI. Defaults to True.
            discrete (bool | None, optional): Whether the metric is discrete. Defaults to False.
            preferred_color (str | None, optional): Optional color hint for the metric in the UI.

        Returns:
            Metric | None: The created metric as a `Metric` model instance, or None on failure.

        Raises:
            NotImplementedError: If `type_` is "SIMULATED" or "CALCULATED" (not supported).
        """
        metric_type = type_.upper()

        if metric_type == "SIMULATED" or metric_type == "CALCULATED":
            metric_type_not_implemented_error = (
                f"Creating metric with type: {type_} is not yet implemented!"
            )
            raise NotImplementedError(metric_type_not_implemented_error)

        if external_id is None:
            external_id = conversions.convert_name_to_external_id(name=name)

        return Metric.from_response(
            self.api.create_metric(
                subject_type_id=str(subject_type_id),
                name=name,
                data_type=data_type.upper(),
                type_=metric_type,
                external_id=external_id,
                mapping_level=mapping_level.upper(),
                unit=unit,
                precision=precision,
                visible=visible,
                discrete=discrete,
                preferred_color=preferred_color,
            )
        )

    def update_metric(
        self,
        metric: Metric,
    ) -> Metric | None:
        """Update an existing metric.

        Args:
            metric (Metric): Metric object with updated fields.

        Returns:
            Metric | None: The updated metric as a `Metric` model instance, or None on failure.
        """
        metric_api_response = self.api.update_metric(
            metric_id=str(metric.id),
            json=metric.to_request(),
        )

        return Metric.from_response(metric_api_response)

    def delete_metric(self, id_: str | UUID) -> None:
        """Delete a metric by ID.

        Args:
            id_ (str | UUID): ID of the metric to delete.
        """
        self.api.delete_metric(metric_id=str(id_))

    def get_subjects(
        self,
        name: str | None = None,
        subject_ids: Sequence[str | UUID] | None = None,
        external_id: str | None = None,
        subject_ids_mode: Literal["SELF", "CHILDREN", "ALL"] | None = None,
        subject_type_ids: Sequence[str | UUID] | None = None,
        property_value_ids: Sequence[str | UUID] | str | UUID | None = None,
    ) -> list[Subject]:
        """Retrieve subjects using a range of optional filters.

        Args:
            name (str | None, optional): Filter by subject name.
            subject_ids (Sequence[str | UUID] | None, optional): Specific subject IDs to fetch.
            external_id (str | None, optional): Filter by external ID.
            subject_ids_mode (Literal | None, optional): Interpretation of `subject_ids`. One of
                "SELF", "CHILDREN", or "ALL".
            subject_type_ids (Sequence[str | UUID] | None, optional): Subject type IDs to filter by.
            property_value_ids (Sequence[str | UUID] | str | UUID | None, optional): Property value IDs to filter on.
                Single IDs are used directly. Sequences use commas for OR (tuples) or semicolons for AND (lists).
                Delimited strings (e.g., "<A>,<B>;<C>") represent (A OR B) AND C. Nested sequences are recursively flattened.

        Returns:
            list[Subject]: A list of `Subject` model instances matching the filters.
        """

        property_value_ids = conversions.convert_property_value_ids_to_query_filter(
            property_value_ids
        )

        subject_responses = self.api.get_subjects(
            name=name,
            subject_ids=conversions.ensure_str_ids(subject_ids),
            subject_ids_mode=subject_ids_mode,
            subject_external_id=external_id,
            subject_type_ids=conversions.ensure_str_ids(subject_type_ids),
            property_value_ids=property_value_ids,
        )

        subject_list: list[Subject] = []
        for subject_response in subject_responses:
            subject = Subject.from_response(subject_response)
            if subject is not None:
                subject_list.append(subject)
        return subject_list

    def get_subject(self, id_: str | UUID) -> Subject | None:
        """Retrieve a single subject by ID.

        Args:
            id_ (str | UUID): The subject ID.

        Returns:
            Subject | None: The `Subject` model instance if found, otherwise None.
        """
        subject_response = self.api.get_subject(subject_id=str(id_))
        return Subject.from_response(subject_response)

    def create_subject(
        self,
        name: str,
        subject_type_id: str | UUID,
        parent_subject_id: str | UUID | None = None,
        properties: Sequence[dict[str, Any] | SubjectProperty] | None = None,
        ingestion_id_overrides: IngestionIdOverride | None = None,
        external_id: str | None = None,
    ) -> Subject | None:
        """Create a new subject.

        Args:
            name (str): Name of the subject.
            subject_type_id (str | UUID): Subject type ID this subject belongs to.
            parent_subject_id (str | UUID | None, optional): Optional parent subject ID.
            properties (Sequence[dict | SubjectProperty] | None, optional): Optional subject properties.
            ingestion_id_overrides (IngestionIdOverride | None, optional): Optional ingestion ID overrides.
            external_id (str | None, optional): External ID for the subject. If None, an external ID is derived from `name`.

        Returns:
            Subject | None: The created `Subject` model instance if successful.
        """
        subject_response = self.api.create_subject(
            name=name,
            parent_subject_id=(
                str(parent_subject_id) if parent_subject_id is not None else None
            ),
            subject_type_id=str(subject_type_id),
            external_id=(
                external_id
                if external_id is not None
                else conversions.convert_name_to_external_id(name=name)
            ),
            ingestion_ids=conversions.convert_ingestion_id_overrides(
                ingestion_id_overrides
            ),  # TODO replace with pydantic method
            properties=(
                [
                    subject_property_adapter.validate_python(p).to_request()
                    for p in properties
                ]
                if properties is not None
                else None
            ),
        )
        # If successful this cannot be 'None'
        return Subject.from_response(subject_response)

    def update_subject(
        self,
        subject: Subject,
    ) -> Subject | None:
        """Update an existing subject.

        Args:
            subject (Subject): A `Subject` model instance with updates applied.

        Returns:
            Subject | None: The updated subject as a `Subject` model instance, or None on failure.
        """

        subject_response = self.api.update_subject(
            subject_id=str(subject.id),
            json=subject.to_request(),
        )

        return Subject.from_response(subject_response)

    def delete_subject(self, id_: str | UUID) -> None:
        """Delete a subject by ID.

        Args:
            id_ (str | UUID): The subject ID to delete.
        """
        self.api.delete_subject(subject_id=str(id_))

    def queue_measurement(
        self,
        ingestion_id: str,
        date: int | float | datetime | str | None = None,
        number: int | float | Decimal | None = None,
        location: dict[str, Any] | Location | None = None,
        text: str | None = None,
    ) -> None:
        """Queue a measurement for later sending.

        The measurement is validated and added to the local ingestion queue. Use `send_measurements`
        to flush queued measurements to the API.

        Args:
            ingestion_id (str): Ingestion ID associated with the measurement.
            date (int | float | datetime | str | None, optional): Timestamp for the measurement. If None, current time is used.
            number (int | float | Decimal | None, optional): Numeric measurement value. Required if `location` is not provided.
            location (dict | Location | None, optional): Location measurement. Required if `number` is not provided.
            text (str | None, optional): Optional text value for the measurement.
        """
        if date is None:
            date = int(time.time() * 1000)

        measurement_dict = {
            "date": date,
            "number": number,
            "location": location,
            "text": text,
        }
        measurement_dict = {k: v for k, v in measurement_dict.items() if v is not None}
        measurement = measurement_adapter.validate_python(measurement_dict)
        self.ingestion_queuer.add_ingestion(
            Ingestion(ingestion_id=ingestion_id, measurement=measurement)
        )

    def send_measurements(self) -> None:
        """Send all queued measurements to the API.

        This method batches queued measurements using the ingestion queuer and sends each batch
        via the underlying API client. After successful sends, the local queue and counts are cleared.
        """
        for series_batch in self.ingestion_queuer.create_series_to_send():
            self.api.send_measurements(series=series_batch.to_request())
        self.ingestion_queuer.clear_stack_and_counts()

    def get_measurements(
        self,
        subject_ids: Sequence[str | UUID] | None = None,
        metric_ids: Sequence[str | UUID] | None = None,
        from_date: datetime | int | float | str | None = None,
        to_date: datetime | int | float | str | None = None,
        size: int | None = None,
        order: str | None = None,
    ) -> list[Series]:
        """Retrieve measurements (series) with filtering options.

        Args:
            subject_ids (Sequence[str | UUID] | None, optional): Subject IDs to filter on. When using `from_date` or `to_date`, this should contain only one subject ID.
            metric_ids (Sequence[str | UUID] | None, optional): Metric IDs to filter on. When using `from_date` or `to_date`, this should contain only one metric ID.
            from_date (datetime | int | float | str | None, optional): Inclusive start date for filtering.
            to_date (datetime | int | float | str | None, optional): Exclusive end date for filtering.
            size (int | None, optional): Page size for the request.
            order (str | None, optional): Order of measurements (based on date).

        Returns:
            list[Series]: A list of `Series` model instances representing the measurements.
        """
        measurements_responses = self.api.get_measurements(
            subject_ids=conversions.ensure_str_ids(subject_ids),
            metric_ids=conversions.ensure_str_ids(metric_ids),
            from_date=conversions.convert_any_date_to_iso8601(from_date),
            to_date=conversions.convert_any_date_to_iso8601(to_date),
            size=size,
            order=order,
        )
        series = []
        if measurements_responses is not None:
            for series_response in measurements_responses.get("series") or []:
                s = Series.from_response(series_response)
                if s is not None:
                    series.append(s)
        return series

    # Event triggers
    def get_event_triggers(
        self,
        name: str | None = None,
    ) -> list[EventTrigger]:
        """Retrieve event triggers, optionally filtered by name.

        Args:
            name (str | None, optional): Filter event triggers by name.

        Returns:
            list[EventTrigger]: A list of `EventTrigger` model instances matching the criteria.
        """
        event_trigger_response_items = self.api.get_event_triggers(
            name=name,
        )
        event_triggers = [
            EventTrigger.from_response(event_trigger_response)
            for event_trigger_response in event_trigger_response_items
            if EventTrigger.from_response(event_trigger_response) is not None
        ]
        return [
            event_trigger
            for event_trigger in event_triggers
            if event_trigger is not None
        ]

    def get_event_trigger(self, id_: str | UUID) -> EventTrigger | None:
        """Retrieve a single event trigger by ID.

        Args:
            id_ (str | UUID): Event trigger ID.

        Returns:
            EventTrigger | None: The `EventTrigger` model instance if found, otherwise None.
        """
        event_trigger_response = self.api.get_event_trigger(event_trigger_id=str(id_))

        return EventTrigger.from_response(event_trigger_response)

    def create_event_trigger(
        self,
        subject_type_id: UUID | str,
        name: str,
        active: bool,
        evaluation_trigger: Literal["INPUT_METRICS", "SUBJECT_METRICS"],
        evaluation_constraint: Literal["NONE", "ALL_TIMESTAMPS_MATCH"],
        event_rules: Sequence[EventRule | dict],
        subject_filter: Sequence[SubjectFilter | dict] | None = None,
    ) -> EventTrigger | None:
        """Create a new event trigger.

        Args:
            subject_type_id (UUID | str): ID of the subject type this trigger applies to.
            name (str): Name of the event trigger.
            active (bool): Whether the event trigger is active.
            evaluation_trigger (Literal): When the trigger is evaluated ("INPUT_METRICS" or "SUBJECT_METRICS").
            evaluation_constraint (Literal): Constraint type ("NONE" or "ALL_TIMESTAMPS_MATCH").
            event_rules (Sequence[EventRule | dict]): List of event rules.
            subject_filter (Sequence[SubjectFilter | dict] | None, optional): Optional subject filter.

        Returns:
            EventTrigger | None: The created `EventTrigger` model instance if successful.
        """
        event_rules_as_dict = [
            (er.to_request() if isinstance(er, EventRule) else er) for er in event_rules
        ]

        if isinstance(subject_filter, SubjectFilter):
            subject_filter_as_dict = subject_filter.to_request()
        elif isinstance(subject_filter, dict):
            subject_filter_as_dict = subject_filter
        else:
            raise TypeError("subject_filter must be of type SubjectFilter or dict")

        return EventTrigger.from_response(
            self.api.create_event_trigger(
                subject_type_id=str(subject_type_id),
                name=name,
                active=active,
                evaluation_trigger=evaluation_trigger,
                evaluation_constraint=evaluation_constraint,
                event_rules=event_rules_as_dict,
                subject_filter=subject_filter_as_dict,
            )
        )

    def update_event_trigger(
        self,
        event_trigger: EventTrigger,
    ) -> EventTrigger | None:
        """Update an existing event trigger.

        Args:
            event_trigger (EventTrigger): `EventTrigger` model instance with updates.

        Returns:
            EventTrigger | None: The updated `EventTrigger` model instance, or None on failure.
        """
        update_event_trigger__api_response = self.api.update_event_trigger(
            event_trigger_id=str(event_trigger.id),
            json=event_trigger.to_request(),
        )

        return EventTrigger.from_response(update_event_trigger__api_response)

    def delete_event_trigger(self, id_: UUID | str) -> None:
        """Delete an event trigger by ID.

        Args:
            id_ (UUID | str): The event trigger ID to delete.
        """
        self.api.delete_event_trigger(event_trigger_id=str(id_))

    # Event
    def get_events(
        self,
        active: bool | None = None,
        suppressed: bool | None = None,
        from_date: datetime | int | float | str | None = None,
        to_date: datetime | int | float | str | None = None,
        only_new: bool | None = None,
        property_value_ids: (
            Sequence[str | UUID | tuple[str | UUID, ...] | list[str | UUID]] | None
        ) = None,
        subject_ids: Sequence[str | UUID] | None = None,
        event_trigger_ids: Sequence[str | UUID] | None = None,
        event_levels: (
            list[Literal["OK", "INFORMATION", "WARNING", "PROBLEM"]] | None
        ) = None,
        sort: str = "startDate,desc",
    ) -> list[Event]:
        """Search and filter events.

        Args:
            active (bool | None, optional): If True, fetch only active events.
            suppressed (bool | None, optional): If True, fetch only suppressed events. If False, fetch only non-suppressed events.
            from_date (datetime | int | float | str | None, optional): Inclusive start date for the search.
            to_date (datetime | int | float | str | None, optional): Exclusive end date for the search.
            only_new (bool | None, optional): If True, only return events that occurred within the given date range.
            property_value_ids (Sequence[str | UUID] | str | UUID | None, optional): Property value IDs to filter on.
                Single IDs are used directly. Sequences use commas for OR (tuples) or semicolons for AND (lists).
                Delimited strings (e.g., "<A>,<B>;<C>") represent (A OR B) AND C. Nested sequences are recursively flattened.
            subject_ids (Sequence[str | UUID] | None, optional): Subject IDs to filter on.
            event_trigger_ids (Sequence[str | UUID] | None, optional): Event trigger IDs to filter on.
            event_levels (list[Literal["OK", "INFORMATION", "WARNING", "PROBLEM"]] | None, optional): Event levels to filter on (e.g., "OK", "WARNING").
            sort (str, optional): Sort order for the results. Defaults to "startDate,desc".

        Returns:
            list[Event]: A list of `Event` model instances matching the search criteria.
        """

        property_value_ids = conversions.convert_property_value_ids_to_query_filter(
            property_value_ids
        )

        converted_subject_ids = conversions.ensure_str_ids(subject_ids)
        event_trigger_ids_str = conversions.ensure_str_ids(event_trigger_ids)

        events_response = self.api.get_events(
            active=active,
            suppressed=suppressed,
            from_date=conversions.convert_any_date_to_iso8601(from_date),
            to_date=conversions.convert_any_date_to_iso8601(to_date),
            only_new=only_new,
            property_value_ids=property_value_ids,
            subject_ids=(
                ",".join(converted_subject_ids)
                if converted_subject_ids is not None
                else None
            ),
            event_trigger_ids=(
                ",".join(event_trigger_ids_str) if event_trigger_ids_str else None
            ),
            event_levels=",".join(event_levels) if event_levels else None,
            sort=sort,
        )
        events = [Event.from_response(event_data) for event_data in events_response]
        return [e for e in events if e]

    def get_event(self, id_: str | UUID) -> Event | None:
        """Retrieve a single event by ID.

        Args:
            id_ (str | UUID): The event ID.

        Returns:
            Event | None: The `Event` model instance if found, otherwise None.
        """
        event_response = self.api.get_event(event_id=str(id_))
        return Event.from_response(event_response) if event_response else None
