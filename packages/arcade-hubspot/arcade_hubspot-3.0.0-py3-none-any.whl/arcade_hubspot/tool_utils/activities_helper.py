"""Helper functions for activity tools."""

from datetime import datetime, timedelta
from typing import Any, Callable, cast

from arcade_hubspot.enums import HubspotActivityType, HubspotObject
from arcade_hubspot.http_client import HubspotHttpClient
from arcade_hubspot.models.tool_models import (
    CreateCallActivityResponse,
    CreateCommunicationActivityResponse,
    CreateEmailActivityResponse,
    CreateMeetingActivityResponse,
    CreateNoteActivityResponse,
)
from arcade_hubspot.tool_utils import shared_utils


def activity_type_to_object(activity_type: HubspotActivityType) -> HubspotObject:
    """Map activity type enum to HubSpot object enum."""
    mapping: dict[HubspotActivityType, HubspotObject] = {
        HubspotActivityType.CALL: HubspotObject.CALL,
        HubspotActivityType.EMAIL: HubspotObject.EMAIL,
        HubspotActivityType.NOTE: HubspotObject.NOTE,
        HubspotActivityType.MEETING: HubspotObject.MEETING,
        HubspotActivityType.TASK: HubspotObject.TASK,
        HubspotActivityType.COMMUNICATION: HubspotObject.COMMUNICATION,
    }
    return mapping[activity_type]


def truncate_string(text: str | None, max_len: int = 100) -> str | None:
    """Truncate a string to max length, adding [...] if truncated."""
    if not text or not isinstance(text, str):
        return text
    if len(text) <= max_len:
        return text
    return text[:max_len] + "[...]"


def create_note_response(resp: dict[str, Any]) -> CreateNoteActivityResponse:
    """Create a note activity response from API response."""
    props = resp.get("properties", {})
    activity_id = resp.get("id") or props.get("hs_object_id")

    response = {
        "id": activity_id,
        "object_type": HubspotObject.NOTE.value,
        "body_preview": props.get("hs_note_body"),
        "owner_id": props.get("hubspot_owner_id"),
        "timestamp": props.get("hs_timestamp"),
    }

    return cast(CreateNoteActivityResponse, response)


def create_call_response(resp: dict[str, Any]) -> CreateCallActivityResponse:
    """Create a call activity response from API response."""
    props = resp.get("properties", {})
    activity_id = resp.get("id") or props.get("hs_object_id")

    response = {
        "id": activity_id,
        "object_type": HubspotObject.CALL.value,
        "title": props.get("hs_call_title"),
        "direction": props.get("hs_call_direction"),
        "status": props.get("hs_call_status"),
        "summary": props.get("hs_call_summary"),
        "owner_id": props.get("hubspot_owner_id"),
        "timestamp": props.get("hs_timestamp"),
    }

    return cast(CreateCallActivityResponse, response)


def create_email_response(resp: dict[str, Any]) -> CreateEmailActivityResponse:
    """Create an email activity response from API response."""
    props = resp.get("properties", {})
    activity_id = resp.get("id") or props.get("hs_object_id")

    response = {
        "id": activity_id,
        "object_type": HubspotObject.EMAIL.value,
        "subject": props.get("hs_email_subject"),
        "status": props.get("hs_email_status"),
        "owner_id": props.get("hubspot_owner_id"),
        "timestamp": props.get("hs_timestamp"),
    }

    return cast(CreateEmailActivityResponse, response)


def create_meeting_response(resp: dict[str, Any]) -> CreateMeetingActivityResponse:
    """Create a meeting activity response from API response."""
    props = resp.get("properties", {})
    activity_id = resp.get("id") or props.get("hs_object_id")

    response = {
        "id": activity_id,
        "object_type": HubspotObject.MEETING.value,
        "title": props.get("hs_meeting_title"),
        "start_time": props.get("hs_meeting_start_time"),
        "end_time": props.get("hs_meeting_end_time"),
        "location": props.get("hs_meeting_location"),
        "outcome": props.get("hs_meeting_outcome"),
        "owner_id": props.get("hubspot_owner_id"),
    }

    return cast(CreateMeetingActivityResponse, response)


def create_communication_response(resp: dict[str, Any]) -> CreateCommunicationActivityResponse:
    """Create a communication activity response from API response."""
    props = resp.get("properties", {})
    activity_id = resp.get("id") or props.get("hs_object_id")

    response = {
        "id": activity_id,
        "object_type": HubspotObject.COMMUNICATION.value,
        "channel": props.get("hs_communication_channel_type"),
        "body_preview": props.get("hs_body_preview"),
        "owner_id": props.get("hubspot_owner_id"),
        "timestamp": props.get("hs_timestamp"),
    }

    return cast(CreateCommunicationActivityResponse, response)


def build_note_update_properties(
    *,
    body: str | None = None,
    when_occurred: str | None = None,
) -> dict[str, object]:
    """Build update payload for note activities."""
    timestamp = shared_utils.to_epoch_millis(when_occurred) if when_occurred else None

    return shared_utils.build_update_properties({
        "hs_note_body": body,
        "hs_timestamp": timestamp,
    })


def build_call_update_properties(
    *,
    title: str | None = None,
    direction: str | None = None,
    summary: str | None = None,
    duration: int | None = None,
    to_number: str | None = None,
    from_number: str | None = None,
    when_occurred: str | None = None,
) -> dict[str, object]:
    """Build update payload for call activities."""
    timestamp = shared_utils.to_epoch_millis(when_occurred) if when_occurred else None

    return shared_utils.build_update_properties({
        "hs_call_title": title,
        "hs_call_direction": direction,
        "hs_call_summary": summary,
        "hs_call_duration": duration,
        "hs_call_to_number": to_number,
        "hs_call_from_number": from_number,
        "hs_timestamp": timestamp,
    })


def build_email_update_properties(
    *,
    subject: str | None = None,
    direction: str | None = None,
    status: str | None = None,
    body_text: str | None = None,
    body_html: str | None = None,
    when_occurred: str | None = None,
) -> dict[str, object]:
    """Build update payload for email activities."""
    timestamp = shared_utils.to_epoch_millis(when_occurred) if when_occurred else None

    return shared_utils.build_update_properties({
        "hs_email_subject": subject,
        "hs_email_direction": direction,
        "hs_email_status": status,
        "hs_email_text": body_text,
        "hs_email_html": body_html,
        "hs_timestamp": timestamp,
    })


def build_meeting_update_properties(
    *,
    title: str | None = None,
    start_date: str | None = None,
    start_time: str | None = None,
    duration: str | None = None,
    location: str | None = None,
    outcome: str | None = None,
) -> dict[str, object]:
    """Build update payload for meeting activities."""
    start_timestamp = _build_meeting_timestamp(start_date, start_time)
    end_timestamp = _add_duration(start_timestamp, duration)

    return shared_utils.build_update_properties({
        "hs_meeting_title": title,
        "hs_meeting_start_time": start_timestamp,
        "hs_timestamp": start_timestamp,
        "hs_meeting_end_time": end_timestamp,
        "hs_meeting_location": location,
        "hs_meeting_outcome": outcome,
    })


def build_communication_update_properties(
    *,
    channel: str | None = None,
    body_text: str | None = None,
    when_occurred: str | None = None,
    logged_from: str | None = None,
) -> dict[str, object]:
    """Build update payload for communication activities."""
    timestamp = shared_utils.to_epoch_millis(when_occurred) if when_occurred else None

    return shared_utils.build_update_properties({
        "hs_communication_channel_type": channel,
        "hs_communication_body": body_text,
        "hs_communication_logged_from": logged_from,
        "hs_timestamp": timestamp,
    })


async def update_activity_record(
    http_client: HubspotHttpClient,
    *,
    activity_object: HubspotObject,
    activity_id: str,
    properties: dict[str, object],
) -> dict[str, Any]:
    """Update an activity via the HubSpot HTTP client."""
    response = await http_client.update_object(
        object_type=activity_object,
        object_id=activity_id,
        properties=properties,
    )
    return dict(response)


async def find_activities_by_keywords(
    http_client: HubspotHttpClient,
    *,
    activity_object: HubspotObject,
    keywords: str,
    limit: int,
) -> list[dict[str, Any]]:
    """Search activities of a given type and return cleaned matches."""
    result = await http_client.search_by_keywords(
        object_type=activity_object,
        keywords=keywords,
        limit=limit,
    )

    if not isinstance(result, dict):
        return []

    return cast(list[dict[str, Any]], result.get(activity_object.plural, []))


def summarize_activity_matches(
    *,
    activity_object: HubspotObject,
    matches: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Summarize activity matches for keyword confirmation responses."""
    summarizer = _ACTIVITY_SUMMARIZERS.get(activity_object)
    if summarizer is None:
        return [_build_generic_activity_summary(match) for match in matches]
    return [summarizer(match) for match in matches]


async def find_association_type_id(
    http_client: Any,
    from_object: HubspotObject,
    to_object: HubspotObject,
) -> str:
    """Find the appropriate association type ID between two HubSpot objects.

    Prioritizes HUBSPOT_DEFINED associations, falls back to first available.
    Raises ToolExecutionError if no association types found.
    """
    from arcade_tdk.errors import ToolExecutionError

    if not hasattr(http_client, "get_association_types"):
        raise ToolExecutionError(
            message="Unable to determine association type",
            developer_message=(
                "The HubSpot client does not expose get_association_types; "
                "retrieve association metadata before calling this helper."
            ),
        )

    types = await http_client.get_association_types(
        from_object=from_object,
        to_object=to_object,
    )

    association_type_id: str | None = None
    if types:
        # First try to find a HUBSPOT_DEFINED association
        for t in types:
            if str(t.get("category")) == "HUBSPOT_DEFINED" and t.get("typeId"):
                association_type_id = str(t["typeId"])
                break
        # Fall back to first available type if no HUBSPOT_DEFINED found
        if not association_type_id and types[0].get("typeId"):
            association_type_id = str(types[0]["typeId"])

    if not association_type_id:
        raise ToolExecutionError(
            message="Unable to determine association type",
            developer_message=(
                f"No association types found between {from_object.value} and {to_object.value}"
            ),
        )

    return association_type_id


def _build_activity_summary(
    activity: dict[str, Any],
    *,
    title_key: str,
    extra_fields: dict[str, str],
    body_preview_key: str | None = None,
) -> dict[str, Any]:
    properties = activity.get("properties", activity)
    summary: dict[str, Any] = {
        "id": str(activity.get("id", "")),
        "title": properties.get(title_key),
    }

    for summary_key, property_key in extra_fields.items():
        summary[summary_key] = properties.get(property_key)

    summary["timestamp"] = summary.get("timestamp") or properties.get("hs_timestamp")

    if body_preview_key:
        body_preview = properties.get(body_preview_key)
        if body_preview:
            summary["body_preview"] = (
                body_preview[:150] + "..." if len(body_preview) > 150 else body_preview
            )

    return summary


def _build_generic_activity_summary(activity: dict[str, Any]) -> dict[str, Any]:
    properties = activity.get("properties", activity)
    return {
        "id": str(activity.get("id", "")),
        "title": properties.get("hs_body_preview"),
        "timestamp": properties.get("hs_timestamp"),
    }


_ACTIVITY_SUMMARIZERS: dict[HubspotObject, Callable[[dict[str, Any]], dict[str, Any]]] = {
    HubspotObject.NOTE: lambda activity: _build_activity_summary(
        activity,
        title_key="hs_body_preview",
        extra_fields={"timestamp": "hs_timestamp"},
        body_preview_key=None,
    ),
    HubspotObject.CALL: lambda activity: _build_activity_summary(
        activity,
        title_key="hs_call_title",
        extra_fields={
            "direction": "hs_call_direction",
            "status": "hs_call_status",
            "timestamp": "hs_timestamp",
        },
        body_preview_key="hs_call_summary",
    ),
    HubspotObject.EMAIL: lambda activity: _build_activity_summary(
        activity,
        title_key="hs_email_subject",
        extra_fields={
            "status": "hs_email_status",
            "timestamp": "hs_timestamp",
        },
        body_preview_key="hs_body_preview",
    ),
    HubspotObject.MEETING: lambda activity: _build_activity_summary(
        activity,
        title_key="hs_meeting_title",
        extra_fields={
            "start_time": "hs_meeting_start_time",
            "end_time": "hs_meeting_end_time",
            "outcome": "hs_meeting_outcome",
            "location": "hs_meeting_location",
        },
        body_preview_key="hs_body_preview",
    ),
    HubspotObject.COMMUNICATION: lambda activity: _build_activity_summary(
        activity,
        title_key="hs_body_preview",
        extra_fields={
            "channel": "hs_communication_channel_type",
            "timestamp": "hs_timestamp",
        },
        body_preview_key="hs_communication_body",
    ),
}


def _build_meeting_timestamp(start_date: str | None, start_time: str | None) -> str | None:
    if not start_date or not start_time:
        return None

    normalized_time = start_time
    if len(start_time.split(":")) == 2:
        normalized_time = f"{start_time}:00"

    try:
        start_datetime = datetime.fromisoformat(f"{start_date}T{normalized_time}")
    except ValueError:
        return None

    return str(int(start_datetime.timestamp() * 1000))


def _add_duration(start_timestamp: str | None, duration: str | None) -> str | None:
    if not start_timestamp or not duration or ":" not in duration:
        return None

    try:
        hours, minutes = map(int, duration.split(":"))
    except ValueError:
        return None

    start_dt = datetime.fromtimestamp(int(start_timestamp) / 1000)
    end_dt = start_dt + timedelta(hours=hours, minutes=minutes)
    return str(int(end_dt.timestamp() * 1000))
