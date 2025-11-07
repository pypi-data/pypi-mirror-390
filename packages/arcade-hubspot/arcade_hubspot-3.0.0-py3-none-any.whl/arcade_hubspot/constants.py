import os

from arcade_hubspot.enums import HubspotObject

HUBSPOT_BASE_URL = "https://api.hubapi.com"
HUBSPOT_CRM_BASE_URL = f"{HUBSPOT_BASE_URL}/crm"
HUBSPOT_DEFAULT_API_VERSION = "v3"

try:
    HUBSPOT_MAX_CONCURRENT_REQUESTS = int(os.getenv("HUBSPOT_MAX_CONCURRENT_REQUESTS", 3))
except ValueError:
    HUBSPOT_MAX_CONCURRENT_REQUESTS = 3

GLOBALLY_IGNORED_FIELDS = [
    "createdate",
    "hs_createdate",
    "hs_lastmodifieddate",
    "lastmodifieddate",
]

CRM_OBJECT_ASSOCIATIONS = [
    HubspotObject.CALL,
    HubspotObject.CONTACT,
    HubspotObject.COMPANY,
    HubspotObject.EMAIL,
    HubspotObject.MEETING,
    HubspotObject.NOTE,
    HubspotObject.TASK,
]

ACTIVITY_ASSOCIATIONS = [
    HubspotObject.CONTACT,
    HubspotObject.COMPANY,
    HubspotObject.DEAL,
]
