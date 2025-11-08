from typing import Any, Sequence, cast
from uuid import UUID

from datetime import datetime, timezone
from dateutil import parser as date_parser

import warnings

from ..models import IngestionIdOverride
from ..util.deprecated import deprecation_warning

warnings.simplefilter("default", DeprecationWarning)


# date conversions


def convert_any_date_to_unix_millis(date: datetime | int | float | str) -> int:
    if isinstance(date, int) or isinstance(date, float):
        try:
            datetime.fromtimestamp(date)
            return int(date * 1000)
        except (ValueError, OSError):
            try:
                # Try to parse the numeric date as epoch milliseconds
                datetime.fromtimestamp(date / 1000)
                return int(date)
            except ValueError as exc:
                raise ValueError(
                    "Cannot parse numeric date as a valid datetime"
                ) from exc

    elif isinstance(date, datetime):
        return int(date.timestamp() * 1000)
    elif isinstance(date, str):
        # Parse the isoformat  string
        try:
            return int(datetime.fromisoformat(date).timestamp() * 1000)
        except ValueError:
            # Parse the string using dateutil.parser
            dt_obj = date_parser.parse(date)
            deprecation_warning(
                "Support for non-ISO date strings will be deprecated in a future version due to performance issues.",
            )
            return int(dt_obj.timestamp() * 1000)
    else:
        raise ValueError("Not a valid type for date")


def convert_any_date_to_iso8601(
    date: datetime | int | float | str | None,
) -> str | None:
    if date is None:
        return None
    unix_millis = convert_any_date_to_unix_millis(date)
    return datetime.fromtimestamp(unix_millis / 1000, tz=timezone.utc).isoformat(
        timespec="milliseconds"
    )


def convert_name_to_external_id(name: str):
    lower_case_name = name.lower()
    external_id = lower_case_name.replace(" ", "-").strip()
    return external_id


def convert_property_value_ids_to_query_filter(
    property_value_ids: (
        str
        | UUID
        | Sequence[str | UUID | tuple[str | UUID, ...] | list[str | UUID]]
        | None
    ),
) -> str | None:
    """Convert property value IDs to a query filter string.

    Handles single IDs, tuples (comma-separated for OR), lists (semicolon-separated for AND),
    strings, UUIDs, and None. Recursively processes nested structures.

    Args:
        property_value_ids: Filter on a list of property value IDs, use a , separator for OR and ; for AND, e.g. <A>,<B>;<C> translates to (A OR B) AND C.

    Returns:
        A string representation of the filter, or None if invalid.
    """
    if isinstance(property_value_ids, (tuple, list)):
        separator = "," if isinstance(property_value_ids, tuple) else ";"
        return separator.join(
            [
                (
                    str(id_)
                    if isinstance(id_, (str, UUID))
                    else cast(str, convert_property_value_ids_to_query_filter(id_))
                )
                for id_ in property_value_ids
            ]
        )
    if isinstance(property_value_ids, (str, UUID)):
        return str(property_value_ids)
    return None


def convert_ingestion_id_overrides(
    ingestion_id_overrides: IngestionIdOverride | None,
) -> list[dict[str, Any]]:
    ingestion_ids = []
    if ingestion_id_overrides is not None:
        for metric_id, ingestion_id in ingestion_id_overrides.items():
            ingestion_ids.append(
                {
                    "metricId": metric_id,
                    "deriveIngestionId": False,
                    "ingestionId": ingestion_id,
                }
            )
    return ingestion_ids


def convert_id(id: str | UUID) -> str | None:
    if id is None:
        return None
    return str(id)


def ensure_str_ids(ids: Sequence[str | UUID] | None) -> list[str] | None:
    if ids is None:
        return None
    return [str(id) for id in ids]
