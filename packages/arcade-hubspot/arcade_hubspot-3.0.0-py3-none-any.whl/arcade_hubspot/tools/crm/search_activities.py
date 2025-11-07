"""Search tools for HubSpot activities."""

from typing import Annotated, Any

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Hubspot

from arcade_hubspot.constants import ACTIVITY_ASSOCIATIONS
from arcade_hubspot.enums import HubspotObject
from arcade_hubspot.http_client.http_client import HubspotHttpClient
from arcade_hubspot.tool_utils import search_activities_helper, shared_utils


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",  # Search for note activities
            "crm.objects.companies.read",  # Associated companies data
            "crm.objects.deals.read",  # Associated deals data
        ],
    ),
)
async def get_note_data_by_keywords(
    context: ToolContext,
    search_terms: Annotated[str, "Search phrase or terms to find in NOTE properties."],
    limit: Annotated[int, "The maximum number of notes to return. Defaults to 10. Max is 50."] = 10,
    associations_limit: Annotated[
        int,
        "The maximum number of each associated object type to return. Defaults to 10.",
    ] = 10,
    truncate_big_strings: Annotated[
        bool,
        "Whether to truncate string properties longer than 100 characters. Defaults to False.",
    ] = False,
    next_page_token: Annotated[
        str | None,
        "The token to get the next page of results. "
        "Defaults to None (returns first page of results)",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "Retrieve note activity data with associated contacts, companies, and deals.",
]:
    """Search for note activities with associated contacts, companies, and deals."""
    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    limit = min(limit, 50)
    result = await http_client.search_by_keywords(
        object_type=HubspotObject.NOTE,
        keywords=search_terms,
        limit=limit,
        next_page_token=next_page_token,
        associations=ACTIVITY_ASSOCIATIONS,
        associations_limit=associations_limit,
    )

    if isinstance(result, dict) and "results" in result:
        should_truncate = truncate_big_strings and len(result["results"]) > 1
        result["results"] = search_activities_helper.truncate_search_results(
            result["results"], should_truncate=should_truncate
        )

    return result if isinstance(result, dict) else {"result": result}


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",  # Search for call activities
            "crm.objects.companies.read",  # Associated companies data
            "crm.objects.deals.read",  # Associated deals data
        ],
    ),
)
async def get_call_data_by_keywords(
    context: ToolContext,
    search_terms: Annotated[str, "Search phrase or terms to find in CALL properties."],
    limit: Annotated[int, "The maximum number of calls to return. Defaults to 10. Max is 50."] = 10,
    associations_limit: Annotated[
        int,
        "The maximum number of each associated object type to return. Defaults to 10.",
    ] = 10,
    truncate_big_strings: Annotated[
        bool,
        "Whether to truncate string properties longer than 100 characters. Defaults to False.",
    ] = False,
    next_page_token: Annotated[
        str | None,
        "The token to get the next page of results. "
        "Defaults to None (returns first page of results)",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "Retrieve call activity data with associated contacts, companies, and deals.",
]:
    """Search for call activities with associated contacts, companies, and deals."""
    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    limit = min(limit, 50)
    result = await http_client.search_by_keywords(
        object_type=HubspotObject.CALL,
        keywords=search_terms,
        limit=limit,
        next_page_token=next_page_token,
        associations=ACTIVITY_ASSOCIATIONS,
        associations_limit=associations_limit,
    )

    # Truncate strings based on parameter and result count
    if isinstance(result, dict) and "results" in result:
        should_truncate = truncate_big_strings and len(result["results"]) > 1
        result["results"] = search_activities_helper.truncate_search_results(
            result["results"], should_truncate=should_truncate
        )

    return result if isinstance(result, dict) else {"result": result}


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",  # Search for email activities
            "crm.objects.companies.read",  # Associated companies data
            "crm.objects.deals.read",  # Associated deals data
        ],
    ),
)
async def get_email_data_by_keywords(
    context: ToolContext,
    search_terms: Annotated[str, "Search phrase or terms to find in EMAIL properties."],
    limit: Annotated[
        int, "The maximum number of emails to return. Defaults to 10. Max is 50."
    ] = 10,
    associations_limit: Annotated[
        int,
        "The maximum number of each associated object type to return. Defaults to 10.",
    ] = 10,
    truncate_big_strings: Annotated[
        bool,
        "Whether to truncate string properties longer than 100 characters. Defaults to False.",
    ] = False,
    next_page_token: Annotated[
        str | None,
        "The token to get the next page of results. "
        "Defaults to None (returns first page of results)",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "Retrieve email activity data with associated contacts, companies, and deals.",
]:
    """Search for email activities with associated contacts, companies, and deals."""
    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    limit = min(limit, 50)
    result = await http_client.search_by_keywords(
        object_type=HubspotObject.EMAIL,
        keywords=search_terms,
        limit=limit,
        next_page_token=next_page_token,
        associations=ACTIVITY_ASSOCIATIONS,
        associations_limit=associations_limit,
    )

    # Truncate strings based on parameter and result count
    if isinstance(result, dict) and "results" in result:
        should_truncate = truncate_big_strings and len(result["results"]) > 1
        result["results"] = search_activities_helper.truncate_search_results(
            result["results"], should_truncate=should_truncate
        )

    return result if isinstance(result, dict) else {"result": result}


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",  # Search for meeting activities
            "crm.objects.companies.read",  # Associated companies data
            "crm.objects.deals.read",  # Associated deals data
        ],
    ),
)
async def get_meeting_data_by_keywords(
    context: ToolContext,
    search_terms: Annotated[str, "Search phrase or terms to find in MEETING properties."],
    limit: Annotated[
        int, "The maximum number of meetings to return. Defaults to 10. Max is 50."
    ] = 10,
    associations_limit: Annotated[
        int,
        "The maximum number of each associated object type to return. Defaults to 10.",
    ] = 10,
    truncate_big_strings: Annotated[
        bool,
        "Whether to truncate string properties longer than 100 characters. Defaults to False.",
    ] = False,
    next_page_token: Annotated[
        str | None,
        "The token to get the next page of results. "
        "Defaults to None (returns first page of results)",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "Retrieve meeting activity data with associated contacts, companies, and deals.",
]:
    """Search for meeting activities with associated contacts, companies, and deals."""
    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    limit = min(limit, 50)
    result = await http_client.search_by_keywords(
        object_type=HubspotObject.MEETING,
        keywords=search_terms,
        limit=limit,
        next_page_token=next_page_token,
        associations=ACTIVITY_ASSOCIATIONS,
        associations_limit=associations_limit,
    )

    # Truncate strings based on parameter and result count
    if isinstance(result, dict) and "results" in result:
        should_truncate = truncate_big_strings and len(result["results"]) > 1
        result["results"] = search_activities_helper.truncate_search_results(
            result["results"], should_truncate=should_truncate
        )

    return result if isinstance(result, dict) else {"result": result}


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",  # Search for task activities
            "crm.objects.companies.read",  # Associated companies data
            "crm.objects.deals.read",  # Associated deals data
        ],
    ),
)
async def get_task_data_by_keywords(
    context: ToolContext,
    search_terms: Annotated[str, "Search phrase or terms to find in TASK properties."],
    limit: Annotated[int, "The maximum number of tasks to return. Defaults to 10. Max is 50."] = 10,
    associations_limit: Annotated[
        int,
        "The maximum number of each associated object type to return. Defaults to 10.",
    ] = 10,
    truncate_big_strings: Annotated[
        bool,
        "Whether to truncate string properties longer than 100 characters. Defaults to False.",
    ] = False,
    next_page_token: Annotated[
        str | None,
        "The token to get the next page of results. "
        "Defaults to None (returns first page of results)",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "Retrieve task activity data with associated contacts, companies, and deals.",
]:
    """Search for task activities with associated contacts, companies, and deals."""
    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    limit = min(limit, 50)
    result = await http_client.search_by_keywords(
        object_type=HubspotObject.TASK,
        keywords=search_terms,
        limit=limit,
        next_page_token=next_page_token,
        associations=ACTIVITY_ASSOCIATIONS,
        associations_limit=associations_limit,
    )

    # Truncate strings based on parameter and result count
    if isinstance(result, dict) and "results" in result:
        should_truncate = truncate_big_strings and len(result["results"]) > 1
        result["results"] = search_activities_helper.truncate_search_results(
            result["results"], should_truncate=should_truncate
        )

    return result if isinstance(result, dict) else {"result": result}


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",  # Search for communication activities
            "crm.objects.companies.read",  # Associated companies data
            "crm.objects.deals.read",  # Associated deals data
        ],
    ),
)
async def get_communication_data_by_keywords(
    context: ToolContext,
    search_terms: Annotated[str, "Search phrase or terms to find in COMMUNICATION properties."],
    limit: Annotated[
        int, "The maximum number of communications to return. Defaults to 10. Max is 50."
    ] = 10,
    associations_limit: Annotated[
        int,
        "The maximum number of each associated object type to return. Defaults to 10.",
    ] = 10,
    truncate_big_strings: Annotated[
        bool,
        "Whether to truncate string properties longer than 100 characters. Defaults to False.",
    ] = False,
    next_page_token: Annotated[
        str | None,
        "The token to get the next page of results. "
        "Defaults to None (returns first page of results)",
    ] = None,
) -> Annotated[
    dict[str, Any],
    "Retrieve communication activity data with associated contacts, companies, and deals.",
]:
    """Search for communication activities with associated contacts, companies, and deals."""
    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    limit = min(limit, 50)
    result = await http_client.search_by_keywords(
        object_type=HubspotObject.COMMUNICATION,
        keywords=search_terms,
        limit=limit,
        next_page_token=next_page_token,
        associations=ACTIVITY_ASSOCIATIONS,
        associations_limit=associations_limit,
    )

    # Truncate strings based on parameter and result count
    if isinstance(result, dict) and "results" in result:
        should_truncate = truncate_big_strings and len(result["results"]) > 1
        result["results"] = search_activities_helper.truncate_search_results(
            result["results"], should_truncate=should_truncate
        )

    return result if isinstance(result, dict) else {"result": result}
