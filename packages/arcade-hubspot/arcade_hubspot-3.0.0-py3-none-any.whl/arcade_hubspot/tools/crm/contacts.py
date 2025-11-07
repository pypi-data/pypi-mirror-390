from typing import Annotated, Any, cast

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Hubspot

from arcade_hubspot.constants import CRM_OBJECT_ASSOCIATIONS
from arcade_hubspot.enums import HubspotObject, HubspotSortOrder
from arcade_hubspot.http_client.http_client import HubspotHttpClient
from arcade_hubspot.models.tool_models import CreateContactResponse, UpdateContactResponse
from arcade_hubspot.tool_utils import contact_utils, shared_utils


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",  # /crm/v3/objects/contacts/search
            "crm.objects.companies.read",  # Associated companies data
            "crm.objects.deals.read",  # Associated deals data
            "sales-email-read",  # Associated email data
        ],
    ),
)
async def get_contact_data_by_keywords(
    context: ToolContext,
    keywords: Annotated[
        str,
        "The keywords to search for contacts. It will match against the contact's "
        "first and last name, email addresses, phone numbers, and company name.",
    ],
    limit: Annotated[
        int, "The maximum number of contacts to return. Defaults to 10. Max is 100."
    ] = 10,
    associations_limit: Annotated[
        int,
        "The maximum number of each associated object type to return. Defaults to 10.",
    ] = 10,
    next_page_token: Annotated[
        str | None,
        "The token to get the next page of results. "
        "Defaults to None (returns first page of results)",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "Retrieve contact data with associated companies, deals, calls, "
    "emails, meetings, notes, and tasks.",
]:
    """
    Retrieve contact data with associated companies, deals, calls, emails,
    meetings, notes, and tasks.
    """
    auth_token = shared_utils.get_auth_token_or_raise(context)

    http_client = HubspotHttpClient(auth_token=auth_token)

    token_info = await http_client.get_current_user_info()
    portal_id = str(token_info["hub_id"]) if token_info.get("hub_id") else None

    limit = min(limit, 100)
    result = await http_client.search_by_keywords(
        object_type=HubspotObject.CONTACT,
        keywords=keywords,
        limit=limit,
        next_page_token=next_page_token,
        portal_id=portal_id,
        associations=CRM_OBJECT_ASSOCIATIONS,
        associations_limit=associations_limit,
    )
    return result if isinstance(result, dict) else {"result": result}


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.write",  # /crm/v3/objects/contacts
        ],
    ),
)
async def create_contact(
    context: ToolContext,
    company_id: Annotated[int, "The ID of the company to create the contact for."],
    first_name: Annotated[str, "The first name of the contact."],
    last_name: Annotated[str | None, "The last name of the contact."] = None,
    email: Annotated[str | None, "The email address of the contact."] = None,
    phone: Annotated[str | None, "The phone number of the contact."] = None,
    mobile_phone: Annotated[str | None, "The mobile phone number of the contact."] = None,
    job_title: Annotated[str | None, "The job title of the contact."] = None,
) -> Annotated[CreateContactResponse, "Create a contact associated with a company."]:
    """Create a contact associated with a company."""
    auth_token = shared_utils.get_auth_token_or_raise(context)

    http_client = HubspotHttpClient(auth_token=auth_token)

    token_info = await http_client.get_current_user_info()
    portal_id = str(token_info["hub_id"]) if token_info.get("hub_id") else None

    response = await http_client.create_contact(
        company_id=str(company_id),
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        mobile_phone=mobile_phone,
        job_title=job_title,
    )

    result = contact_utils.create_contact_response(dict(response), portal_id)
    return result


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",  # Needed for keyword searches
            "crm.objects.contacts.write",  # Required to update contacts
        ],
    ),
)
async def update_contact(
    context: ToolContext,
    contact_id: Annotated[int | None, "The ID of the contact to update."] = None,
    keywords: Annotated[
        str | None,
        (
            "Keywords to search for the contact (name, email, phone). "
            "Provide when contact_id is not known."
        ),
    ] = None,
    first_name: Annotated[str | None, "The first name of the contact."] = None,
    last_name: Annotated[str | None, "The last name of the contact."] = None,
    email: Annotated[str | None, "The email address of the contact."] = None,
    phone: Annotated[str | None, "The phone number of the contact."] = None,
    mobile_phone: Annotated[str | None, "The mobile phone number of the contact."] = None,
    job_title: Annotated[str | None, "The job title of the contact."] = None,
    matches_limit: Annotated[
        int,
        (
            "The maximum number of contacts to return when searching by keywords. "
            "Defaults to 5. Max is 20."
        ),
    ] = 5,
) -> Annotated[
    UpdateContactResponse,
    "Update a contact by ID or list matching contacts when searching by keywords.",
]:
    """Update a contact directly by ID or list possible matches when searching by keywords."""
    shared_utils.ensure_single_identifier(
        entity_name="contact", identifier=contact_id, keywords=keywords
    )

    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    token_info = await http_client.get_current_user_info()
    portal_id = str(token_info.get("hub_id")) if token_info.get("hub_id") else None

    if keywords is not None:
        capped_limit = shared_utils.cap_results_limit(
            requested_limit=matches_limit,
            default_limit=5,
            max_limit=20,
        )
        matches = await contact_utils.find_contacts_by_keywords(
            http_client=http_client,
            keywords=keywords,
            limit=capped_limit,
            portal_id=portal_id,
        )

        summaries = contact_utils.summarize_contact_matches(matches)
        return cast(
            UpdateContactResponse,
            shared_utils.build_keyword_confirmation_response(
                entity_name="contact",
                keywords=keywords,
                matches=summaries,
                limit=capped_limit,
            ),
        )

    properties = contact_utils.build_contact_properties(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        mobile_phone=mobile_phone,
        job_title=job_title,
    )

    updated = await contact_utils.update_contact_record(
        http_client=http_client,
        contact_id=str(contact_id),
        properties=properties,
    )

    contact_payload = contact_utils.create_contact_response(updated, portal_id)
    return cast(UpdateContactResponse, contact_payload)


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",  # /crm/v3/objects/contacts/search
            "crm.objects.companies.read",  # Associated companies data
            "crm.objects.deals.read",  # Associated deals data
            "sales-email-read",  # Associated email data
        ],
    ),
)
async def list_contacts(
    context: ToolContext,
    limit: Annotated[
        int, "The maximum number of contacts to return. Defaults to 10. Max is 50."
    ] = 10,
    associations_limit: Annotated[
        int,
        "The maximum number of each associated object type to return. Defaults to 10.",
    ] = 10,
    company_id: Annotated[
        int | None, "Filter contacts by company ID. Defaults to None (no filtering)."
    ] = None,
    deal_id: Annotated[
        int | None, "Filter contacts by deal ID. Defaults to None (no filtering)."
    ] = None,
    sort_order: Annotated[
        HubspotSortOrder, "Sort order for results. Defaults to LATEST_MODIFIED."
    ] = HubspotSortOrder.LATEST_MODIFIED,
    next_page_token: Annotated[
        str | None,
        "The token to get the next page of results. "
        "Defaults to None (returns first page of results)",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "List contacts with associated companies, deals, calls, emails, meetings, notes, and tasks.",
]:
    """List contacts with associated companies, deals, calls, emails, meetings, notes, and tasks."""
    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    token_info = await http_client.get_current_user_info()
    portal_id = str(token_info["hub_id"]) if token_info.get("hub_id") else None

    limit = min(limit, 50)

    result = await http_client.list_objects_with_filters(
        object_type=HubspotObject.CONTACT,
        limit=limit,
        company_id=str(company_id) if company_id is not None else None,
        deal_id=str(deal_id) if deal_id is not None else None,
        sort_order=sort_order,
        next_page_token=next_page_token,
        associations=CRM_OBJECT_ASSOCIATIONS,
        associations_limit=associations_limit,
        portal_id=portal_id,
    )

    return result if isinstance(result, dict) else {"result": result}
