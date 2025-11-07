"""Utility functions for company operations."""

from typing import Any, cast

from arcade_tdk.errors import RetryableToolError

from arcade_hubspot.enums import HubspotIndustryType, HubspotObject
from arcade_hubspot.http_client import HubspotHttpClient
from arcade_hubspot.models.tool_models import CreateCompanyResponse
from arcade_hubspot.tool_utils import shared_utils
from arcade_hubspot.utils.gui_url_builder import build_company_gui_url


async def create_company_record(
    http_client: HubspotHttpClient,
    name: str,
    domain: str | None = None,
    industry: str | None = None,
    city: str | None = None,
    state: str | None = None,
    country: str | None = None,
    phone: str | None = None,
    website: str | None = None,
) -> dict[str, Any]:
    """
    Create a company record in HubSpot via the HTTP client.

    Args:
        http_client: HubSpot HTTP client
        name: Company name (required)
        domain: Company domain
        industry: Company industry
        city: Company city
        state: Company state
        country: Company country
        phone: Company phone number
        website: Company website

    Returns:
        HubSpot API response with created company information.
    """
    response = await http_client.create_company(
        name=name,
        domain=domain,
        industry=industry,
        city=city,
        state=state,
        country=country,
        phone=phone,
        website=website,
    )
    return dict(response)


def create_company_response(
    company_data: dict[str, Any], portal_id: str | None = None
) -> CreateCompanyResponse:
    """
    Create a standardized response for company creation operations.

    Args:
        company_data: Raw company data from HubSpot API

    Returns:
        Cleaned company response for tool output.
    """
    properties = company_data.get("properties", {})

    # Build GUI URL if portal_id is available
    company_gui_url = None
    if portal_id and company_data.get("id"):
        company_id = str(company_data.get("id"))
        company_gui_url = build_company_gui_url(portal_id, company_id)

    # Build response data
    response_data: CreateCompanyResponse = {
        "id": str(company_data.get("id", "")),
        "name": properties.get("name"),
        "domain": properties.get("domain"),
        "industry": properties.get("industry"),
        "city": properties.get("city"),
        "state": properties.get("state"),
        "country": properties.get("country"),
        "phone": properties.get("phone"),
        "website": properties.get("website"),
        "created_at": company_data.get("createdAt"),
        "company_gui_url": company_gui_url,
    }

    return response_data


def build_company_properties(
    *,
    company_name: str | None = None,
    web_domain: str | None = None,
    industry_type: str | None = None,
    company_city: str | None = None,
    company_state: str | None = None,
    company_country: str | None = None,
    phone_number: str | None = None,
    website_url: str | None = None,
) -> dict[str, object]:
    """Build HubSpot company property payload for updates."""
    normalized_industry = validate_and_normalize_industry_type(industry_type)

    return shared_utils.build_update_properties({
        "name": company_name,
        "domain": web_domain,
        "industry": normalized_industry,
        "city": company_city,
        "state": company_state,
        "country": company_country,
        "phone": phone_number,
        "website": website_url,
    })


async def update_company_record(
    http_client: HubspotHttpClient,
    *,
    company_id: str,
    properties: dict[str, object],
) -> dict[str, Any]:
    """Update a company via the HubSpot HTTP client."""
    response = await http_client.update_company(company_id=company_id, properties=properties)
    return dict(response)


async def find_companies_by_keywords(
    http_client: HubspotHttpClient,
    *,
    keywords: str,
    limit: int,
    portal_id: str | None = None,
) -> list[dict[str, Any]]:
    """Search companies and return cleaned matches."""
    result = await http_client.search_by_keywords(
        object_type=HubspotObject.COMPANY,
        keywords=keywords,
        limit=limit,
        portal_id=portal_id,
    )

    if not isinstance(result, dict):
        return []

    return cast(list[dict[str, Any]], result.get(HubspotObject.COMPANY.plural, []))


def summarize_company_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Summarize company matches for keyword confirmation responses."""
    return [_build_company_summary(match) for match in matches]


def validate_and_normalize_industry_type(industry_type: str | None) -> str | None:
    """Validate and normalize industry type input.

    Args:
        industry_type: The industry type string to validate (case-insensitive)

    Returns:
        The normalized industry type value or None if input is None

    Raises:
        RetryableToolError: If the industry type is invalid
    """
    if industry_type is None:
        return None

    industry_map = {industry.value.upper(): industry.value for industry in HubspotIndustryType}
    normalized_input = industry_type.upper()

    if normalized_input in industry_map:
        return industry_map[normalized_input]

    valid_industries = sorted([industry.value for industry in HubspotIndustryType])
    raise RetryableToolError(
        message=f"Invalid industry type '{industry_type}'.",
        additional_prompt_content=(
            f"The industry type '{industry_type}' is not valid. "
            f"Please use one of the following valid industry types (case-insensitive):\n"
            f"{', '.join(valid_industries)}"
        ),
    )


def _build_company_summary(company_data: dict[str, Any]) -> dict[str, Any]:
    properties = company_data.get("properties", company_data)
    return {
        "id": str(company_data.get("id", "")),
        "name": properties.get("name"),
        "domain": properties.get("domain"),
        "website": properties.get("website"),
        "phone": properties.get("phone"),
        "industry": properties.get("industry"),
        "city": properties.get("city"),
        "state": properties.get("state"),
        "country": properties.get("country"),
    }
