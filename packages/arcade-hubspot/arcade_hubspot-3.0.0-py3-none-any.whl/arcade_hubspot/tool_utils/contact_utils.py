"""Utility functions for contact operations."""

from typing import Any, cast

from arcade_hubspot.enums import HubspotObject
from arcade_hubspot.http_client import HubspotHttpClient
from arcade_hubspot.models.tool_models import CreateContactResponse
from arcade_hubspot.tool_utils import shared_utils
from arcade_hubspot.utils.gui_url_builder import build_contact_gui_url


def create_contact_response(
    contact_data: dict[str, Any], portal_id: str | None = None
) -> CreateContactResponse:
    """
    Create a standardized response for contact creation operations.

    Args:
        contact_data: Raw contact data from HubSpot API
        portal_id: HubSpot portal ID for GUI URL generation

    Returns:
        Cleaned contact response for tool output.
    """
    properties = contact_data.get("properties", {})

    # Build GUI URL if portal_id is available
    contact_gui_url = None
    if portal_id and contact_data.get("id"):
        contact_id = str(contact_data.get("id"))
        contact_gui_url = build_contact_gui_url(portal_id, contact_id)

    # Build response data
    response_data: CreateContactResponse = {
        "id": str(contact_data.get("id", "")),
        "object_type": contact_data.get("object_type", "contact"),
        "firstname": properties.get("firstname"),
        "lastname": properties.get("lastname"),
        "email_address": properties.get("email"),
        "phone": properties.get("phone"),
        "mobilephone": properties.get("mobilephone"),
        "jobtitle": properties.get("jobtitle"),
        "contact_gui_url": contact_gui_url,
    }

    return response_data


def build_contact_properties(
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    phone: str | None = None,
    mobile_phone: str | None = None,
    job_title: str | None = None,
) -> dict[str, object]:
    """Build HubSpot contact property payload for updates."""
    return shared_utils.build_update_properties({
        "firstname": first_name,
        "lastname": last_name,
        "email": email,
        "phone": phone,
        "mobilephone": mobile_phone,
        "jobtitle": job_title,
    })


async def update_contact_record(
    http_client: HubspotHttpClient,
    *,
    contact_id: str,
    properties: dict[str, object],
) -> dict[str, Any]:
    """Update a contact via the HubSpot HTTP client."""
    response = await http_client.update_contact(contact_id=contact_id, properties=properties)
    return dict(response)


async def find_contacts_by_keywords(
    http_client: HubspotHttpClient,
    *,
    keywords: str,
    limit: int,
    portal_id: str | None = None,
) -> list[dict[str, Any]]:
    """Search contacts and return cleaned matches."""
    result = await http_client.search_by_keywords(
        object_type=HubspotObject.CONTACT,
        keywords=keywords,
        limit=limit,
        portal_id=portal_id,
    )

    if not isinstance(result, dict):
        return []

    return cast(list[dict[str, Any]], result.get(HubspotObject.CONTACT.plural, []))


def summarize_contact_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize contact matches for keyword confirmation responses."""
    return [_build_contact_summary(match) for match in matches]


def _build_contact_summary(contact_data: dict[str, Any]) -> dict[str, Any]:
    properties = contact_data.get("properties", contact_data)
    full_name = shared_utils.build_full_name(
        properties.get("firstname"), properties.get("lastname")
    )
    return {
        "id": str(contact_data.get("id", "")),
        "name": full_name,
        "firstname": properties.get("firstname"),
        "lastname": properties.get("lastname"),
        "email": properties.get("email") or properties.get("email_address"),
        "phone": properties.get("phone"),
        "mobilephone": properties.get("mobilephone"),
        "job_title": properties.get("jobtitle"),
        "lifecyclestage": properties.get("lifecyclestage"),
    }
