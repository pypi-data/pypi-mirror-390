from typing import (
    Any,
)

from uuid import UUID

from pydantic import field_validator

from .subject_property import SubjectProperty

from .utils import remove_property_value_if_id_exists

from .base import BlockbaxModel

from .type_hints import (
    BlockbaxDatetime,
)

from .subject_property import subject_property_adapter


class IngestionDetails(BlockbaxModel):
    metric_id: UUID
    derive_ingestion_id: bool = False
    ingestion_id: str | None = None


class Subject(BlockbaxModel):
    id: UUID
    name: str
    subject_type_id: UUID
    external_id: str
    created_date: BlockbaxDatetime
    properties: list[SubjectProperty] = []
    ingestion_ids: list[IngestionDetails] = []
    updated_date: BlockbaxDatetime | None = None
    parent_subject_id: UUID | None = None
    # lazy-loaded map of property_type_id to property for faster lookup be the class methods
    # Leading underscore ensures this attribute is NOT included in the model schema; as expected
    _property_type_id_to_property: dict[UUID, SubjectProperty] | None = None

    @classmethod  # type: ignore
    @field_validator("properties", mode="before")
    def convert_dict_properties_to_subject_property(
        cls, v: list[SubjectProperty | dict[Any, Any]]
    ) -> list[SubjectProperty]:
        """
        On creation of the model converts dict type properties to SubjectProperty object
        """
        transformed_properties_list: list[SubjectProperty] = []
        for subject_property in v:
            if isinstance(subject_property, dict):
                transformed_properties_list.append(
                    subject_property_adapter.validate_python(subject_property)
                )
            else:
                transformed_properties_list.append(subject_property)
        return transformed_properties_list

    def to_request(self) -> dict[str, Any]:
        subject_dump = self.model_dump(by_alias=True, exclude_none=True, mode="json")
        properties_dump = subject_dump["properties"]
        # The following is a workaround for when a property has predefined values, where currently
        # passing both of the value id and value results in an error from the API
        cleaned_properties = []
        for property_dump in properties_dump:
            if "valueId" in property_dump:
                property_dump = remove_property_value_if_id_exists(property_dump)
                if property_dump.get("inherit"):
                    # valueId cannot exist when inheriting
                    del property_dump["valueId"]
            cleaned_properties.append(property_dump)

        subject_dump["properties"] = cleaned_properties

        # The API returns both the ingestion Id and the deriveIngestionId flag
        # If the deriveIngestionId flag is set the ingestion ID cannot be passed
        new_ingestion_details = []
        for ingestion_details in subject_dump["ingestionIds"]:
            if (
                "deriveIngestionId" in ingestion_details
                and ingestion_details["deriveIngestionId"] is True
                and "ingestionId" in ingestion_details
            ):
                del ingestion_details["ingestionId"]
            new_ingestion_details.append(ingestion_details)

        subject_dump["ingestionIds"] = new_ingestion_details

        return subject_dump

    def lazy_set_properties_map(self):
        """
        Populates the map of subject_type_id to property from list of properties for faster lookup
        Lazy-loaded for faster performance in case of large number of properties
        !Be careful to update the map on the methods that modifies properties
        """
        if self._property_type_id_to_property is None:
            self._property_type_id_to_property = dict(
                (subject_property.type_id, subject_property)
                for subject_property in self.properties
            )

    def set_properties(
        self, properties: list[dict[Any, Any] | SubjectProperty]
    ) -> None:
        """Store property values in the properties attribute."""
        self.lazy_set_properties_map()
        assert (
            self._property_type_id_to_property is not None
        ), "Ensure lazy loaded property type map is populated. This is most likely a bug in the SDK"
        for new_prop in properties:
            new_prop = subject_property_adapter.validate_python(new_prop)
            self._property_type_id_to_property[new_prop.type_id] = new_prop
        self.properties = list(self._property_type_id_to_property.values())

    def remove_properties(self, property_type_ids: list[UUID | str]) -> None:
        """Remove a property value from the properties attribute."""
        property_type_ids_to_remove = [
            (
                UUID(property_type_id)
                if isinstance(property_type_id, str)
                else property_type_id
            )
            for property_type_id in property_type_ids
        ]
        self.properties = [
            prop
            for prop in self.properties
            if prop.type_id not in property_type_ids_to_remove
        ]

    def get_property_by_type_id(
        self, property_type_id: UUID | str
    ) -> SubjectProperty | None:
        """
        Args:
            property_type_id (UUID|str): Property type id to look up in the properties list
        """
        self.lazy_set_properties_map()
        if isinstance(property_type_id, str):
            property_type_id = UUID(property_type_id)
        assert (
            self._property_type_id_to_property is not None
        ), "Ensure lazy loaded property type map is populated. This is most likely a bug in the SDK"
        return self._property_type_id_to_property.get(property_type_id, None)

    def override_ingestion_id(self, metric_id: UUID | str, ingestion_id: str) -> None:
        """Stored an ingestion ID to override in ingestion_ids attribute per metric ID and sets deriveIngestionId to False."""
        if isinstance(metric_id, str):
            metric_id = UUID(metric_id)
        for ingestion in self.ingestion_ids:
            if metric_id == ingestion.metric_id:
                ingestion.ingestion_id = ingestion_id
                ingestion.derive_ingestion_id = False

    def derive_ingestion_id(self, metric_id: UUID | str):
        """Remove an ingestion ID to override in ingestion_ids attribute per metric ID and sets deriveIngestionId to True."""
        if isinstance(metric_id, str):
            metric_id = UUID(metric_id)
        for ingestion in self.ingestion_ids:
            if metric_id == ingestion.metric_id:
                ingestion.ingestion_id = None
                ingestion.derive_ingestion_id = True

    def get_ingestion_id(self, metric_id: UUID | str) -> str | None:
        """
        Get the first matched ingestion id with a specific metric id.
        Args:
            metric_id (UUID| str)

        Returns:
            str|None
        """
        if isinstance(metric_id, str):
            metric_id = UUID(metric_id)
        for ingestion in self.ingestion_ids:
            if metric_id == ingestion.metric_id:
                return ingestion.ingestion_id
        return None

    def get_metric_id(self, ingestion_id: str) -> UUID | None:
        """
        Get the metric id of an ingestion id.
        Args:
            ingestion_id (str)

        Returns:
            str|None
        """
        for ingestion in self.ingestion_ids:
            if ingestion_id == ingestion.ingestion_id:
                return ingestion.metric_id
        return None

    def has_ingestion_ids(self, ingestion_ids: list[str]) -> bool:
        """
        If the subject has all passed ingestion ids.
        Args:
            ingestion_ids (list[str])

        Returns:
            bool
        """
        return all(
            ingestion_id
            in [known_ingestion.ingestion_id for known_ingestion in self.ingestion_ids]
            for ingestion_id in ingestion_ids
        )

    def has_ingestion_id(self, ingestion_id: str) -> bool:
        """
        If the subject has a specific passed ingestion id.
        Args:
            ingestion_id (str)

        Returns:
            bool
        """
        return any(
            ingestion_id == ingestion.ingestion_id for ingestion in self.ingestion_ids
        )

    def has_metric_id(self, metric_id: UUID | str) -> bool:
        """
        If the subject has an ingestion id with the passed metric id.
        Args:
            metric_id (UUID| str)

        Returns:
            bool
        """
        if isinstance(metric_id, str):
            metric_id = UUID(metric_id)
        return any(metric_id == ingestion.metric_id for ingestion in self.ingestion_ids)
