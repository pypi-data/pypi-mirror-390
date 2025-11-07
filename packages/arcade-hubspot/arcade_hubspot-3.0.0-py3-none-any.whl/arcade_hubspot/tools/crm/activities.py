from typing import Annotated, Any, cast

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Hubspot

from arcade_hubspot.enums import (
    HubspotActivityType,
    HubspotCallDirection,
    HubspotCommunicationChannel,
    HubspotEmailDirection,
    HubspotEmailStatus,
    HubspotMeetingOutcome,
    HubspotObject,
)
from arcade_hubspot.http_client.http_client import HubspotHttpClient
from arcade_hubspot.models.tool_models import (
    CreateCallActivityResponse,
    CreateCommunicationActivityResponse,
    CreateEmailActivityResponse,
    CreateMeetingActivityResponse,
    CreateNoteActivityResponse,
    UpdateCallActivityResponse,
    UpdateCommunicationActivityResponse,
    UpdateEmailActivityResponse,
    UpdateMeetingActivityResponse,
    UpdateNoteActivityResponse,
)
from arcade_hubspot.tool_utils import activities_helper, shared_utils


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.write",  # Write access for CRM objects including activities
        ],
    ),
)
async def create_note_activity(
    context: ToolContext,
    body: Annotated[str, "The note content/body."],
    when_occurred: Annotated[
        str,
        "When the note was created (ISO date format: YYYY-MM-DDTHH:MM:SS).",
    ],
    associate_to_contact_id: Annotated[
        int | None,
        "Contact ID to associate this note with.",
    ] = None,
    associate_to_company_id: Annotated[
        int | None,
        "Company ID to associate this note with.",
    ] = None,
    associate_to_deal_id: Annotated[
        int | None,
        "Deal ID to associate this note with.",
    ] = None,
) -> Annotated[
    CreateNoteActivityResponse,
    "Details of the note engagement activity created.",
]:
    """
    Create a note engagement activity with required owner and associations.
    Must be associated with at least one of: contact, company, or deal.
    Assign to the current user if not specified otherwise.
    """
    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    my_hubspot_id = await shared_utils.get_current_hubspot_user_id(context)

    epoch = int(shared_utils.to_epoch_millis(when_occurred))
    resp = await http_client.create_note(
        body=body,
        owner_id=str(my_hubspot_id),
        timestamp=epoch,
        contact_ids=[str(associate_to_contact_id)] if associate_to_contact_id else None,
        company_ids=[str(associate_to_company_id)] if associate_to_company_id else None,
        deal_ids=[str(associate_to_deal_id)] if associate_to_deal_id else None,
    )
    result = activities_helper.create_note_response(resp)
    return result


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",  # Required for keyword searches
            "crm.objects.contacts.write",  # Required to update activities
        ],
    ),
)
async def update_note_activity(
    context: ToolContext,
    note_id: Annotated[int | None, "The note ID to update."] = None,
    keywords: Annotated[
        str | None,
        "Keywords to search for the note content. Provide when note_id is not known.",
    ] = None,
    body: Annotated[str | None, "Updated note content."] = None,
    when_occurred: Annotated[
        str | None,
        "Updated creation timestamp (ISO format: YYYY-MM-DDTHH:MM:SS).",
    ] = None,
    matches_limit: Annotated[
        int,
        ("Maximum number of notes to return when searching by keywords. Defaults to 5. Max is 20."),
    ] = 5,
) -> Annotated[
    UpdateNoteActivityResponse,
    "Update a note by ID or list matching notes when searching by keywords.",
]:
    """Update a note directly by ID or surface matches when searching by keywords."""
    shared_utils.ensure_single_identifier(
        entity_name="note_activity", identifier=note_id, keywords=keywords
    )

    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    if keywords is not None:
        capped_limit = shared_utils.cap_results_limit(
            requested_limit=matches_limit,
            default_limit=5,
            max_limit=20,
        )
        matches = await activities_helper.find_activities_by_keywords(
            http_client=http_client,
            activity_object=HubspotObject.NOTE,
            keywords=keywords,
            limit=capped_limit,
        )

        summaries = activities_helper.summarize_activity_matches(
            activity_object=HubspotObject.NOTE,
            matches=matches,
        )
        return cast(
            UpdateNoteActivityResponse,
            shared_utils.build_keyword_confirmation_response(
                entity_name="note_activity",
                keywords=keywords,
                matches=summaries,
                limit=capped_limit,
            ),
        )

    properties = activities_helper.build_note_update_properties(
        body=body,
        when_occurred=when_occurred,
    )

    updated = await activities_helper.update_activity_record(
        http_client=http_client,
        activity_object=HubspotObject.NOTE,
        activity_id=str(note_id),
        properties=properties,
    )

    return cast(UpdateNoteActivityResponse, activities_helper.create_note_response(updated))


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.write",  # Write access for CRM objects including activities
        ],
    ),
)
async def create_call_activity(
    context: ToolContext,
    title: Annotated[str, "Short title for the call."],
    when_occurred: Annotated[
        str,
        "When the call occurred (ISO date format: YYYY-MM-DDTHH:MM:SS).",
    ],
    direction: Annotated[
        HubspotCallDirection | None,
        "Call direction (INBOUND or OUTBOUND).",
    ] = None,
    summary: Annotated[
        str | None,
        "Short summary/notes of the call.",
    ] = None,
    duration: Annotated[
        int | None,
        "Call duration in seconds.",
    ] = None,
    to_number: Annotated[
        str | None,
        "Phone number called to.",
    ] = None,
    from_number: Annotated[
        str | None,
        "Phone number called from.",
    ] = None,
    associate_to_contact_id: Annotated[
        int | None,
        "Contact ID to associate this call with.",
    ] = None,
    associate_to_company_id: Annotated[
        int | None,
        "Company ID to associate this call with.",
    ] = None,
    associate_to_deal_id: Annotated[
        int | None,
        "Deal ID to associate this call with.",
    ] = None,
) -> Annotated[
    CreateCallActivityResponse,
    "Details of the call engagement activity created.",
]:
    """
    Create a call engagement activity with required owner and associations.
    Must be associated with at least one of: contact, company, or deal.
    Assign to the current user if not specified otherwise.
    """
    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    my_hubspot_id = await shared_utils.get_current_hubspot_user_id(context)

    epoch = int(shared_utils.to_epoch_millis(when_occurred))
    resp = await http_client.create_call(
        title=title,
        owner_id=str(my_hubspot_id),
        direction=direction.value if direction else None,
        summary=summary,
        duration=duration,
        to_number=to_number,
        from_number=from_number,
        timestamp=epoch,
        contact_ids=[str(associate_to_contact_id)] if associate_to_contact_id else None,
        company_ids=[str(associate_to_company_id)] if associate_to_company_id else None,
        deal_ids=[str(associate_to_deal_id)] if associate_to_deal_id else None,
    )
    result = activities_helper.create_call_response(resp)
    return result


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",
            "crm.objects.contacts.write",
        ],
    ),
)
async def update_call_activity(
    context: ToolContext,
    call_id: Annotated[int | None, "The call activity ID to update."] = None,
    keywords: Annotated[
        str | None,
        "Keywords to search for call summaries or titles. Provide when call_id is not known.",
    ] = None,
    title: Annotated[str | None, "Updated call title."] = None,
    direction: Annotated[HubspotCallDirection | None, "Updated call direction."] = None,
    summary: Annotated[str | None, "Updated call summary."] = None,
    duration: Annotated[int | None, "Updated call duration in seconds."] = None,
    to_number: Annotated[str | None, "Updated number called to."] = None,
    from_number: Annotated[str | None, "Updated number called from."] = None,
    when_occurred: Annotated[
        str | None,
        "Updated call timestamp (ISO format: YYYY-MM-DDTHH:MM:SS).",
    ] = None,
    matches_limit: Annotated[
        int,
        ("Maximum number of calls to return when searching by keywords. Defaults to 5. Max is 20."),
    ] = 5,
) -> Annotated[
    UpdateCallActivityResponse,
    "Update a call by ID or list matching calls when searching by keywords.",
]:
    """Update a call activity directly by ID or surface matches when searching by keywords."""
    shared_utils.ensure_single_identifier(
        entity_name="call_activity", identifier=call_id, keywords=keywords
    )

    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    if keywords is not None:
        capped_limit = shared_utils.cap_results_limit(
            requested_limit=matches_limit,
            default_limit=5,
            max_limit=20,
        )
        matches = await activities_helper.find_activities_by_keywords(
            http_client=http_client,
            activity_object=HubspotObject.CALL,
            keywords=keywords,
            limit=capped_limit,
        )

        summaries = activities_helper.summarize_activity_matches(
            activity_object=HubspotObject.CALL,
            matches=matches,
        )
        return cast(
            UpdateCallActivityResponse,
            shared_utils.build_keyword_confirmation_response(
                entity_name="call_activity",
                keywords=keywords,
                matches=summaries,
                limit=capped_limit,
            ),
        )

    normalized_direction = (
        direction.value if isinstance(direction, HubspotCallDirection) else direction
    )

    properties = activities_helper.build_call_update_properties(
        title=title,
        direction=normalized_direction,
        summary=summary,
        duration=duration,
        to_number=to_number,
        from_number=from_number,
        when_occurred=when_occurred,
    )

    updated = await activities_helper.update_activity_record(
        http_client=http_client,
        activity_object=HubspotObject.CALL,
        activity_id=str(call_id),
        properties=properties,
    )

    return cast(UpdateCallActivityResponse, activities_helper.create_call_response(updated))


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.write",  # Write access for CRM objects including activities
        ],
    ),
)
async def create_email_activity(
    context: ToolContext,
    subject: Annotated[str, "Email subject."],
    when_occurred: Annotated[
        str,
        "When the email occurred (ISO date format: YYYY-MM-DDTHH:MM:SS).",
    ],
    from_email: Annotated[str, "Sender email address."],
    to_email: Annotated[str, "Primary recipient email address."],
    body_text: Annotated[str | None, "Email body in plain text."] = None,
    body_html: Annotated[str | None, "Email body in HTML format."] = None,
    from_first_name: Annotated[str | None, "Sender first name."] = None,
    from_last_name: Annotated[str | None, "Sender last name."] = None,
    to_first_name: Annotated[str | None, "Primary recipient first name."] = None,
    to_last_name: Annotated[str | None, "Primary recipient last name."] = None,
    cc_emails: Annotated[
        list[str] | None,
        "CC recipient email addresses.",
    ] = None,
    bcc_emails: Annotated[
        list[str] | None,
        "BCC recipient email addresses.",
    ] = None,
    direction: Annotated[
        HubspotEmailDirection | None,
        "Direction the email was sent (EMAIL, INCOMING_EMAIL, FORWARDED_EMAIL).",
    ] = HubspotEmailDirection.EMAIL,
    status: Annotated[
        HubspotEmailStatus | None,
        "Email status indicating the state of the email.",
    ] = None,
    associate_to_contact_id: Annotated[
        int | None,
        "Contact ID to associate this email with.",
    ] = None,
    associate_to_company_id: Annotated[
        int | None,
        "Company ID to associate this email with.",
    ] = None,
    associate_to_deal_id: Annotated[
        int | None,
        "Deal ID to associate this email with.",
    ] = None,
) -> Annotated[
    CreateEmailActivityResponse,
    "Details of the email engagement activity created.",
]:
    """
    Create a logged email engagement activity with essential fields including email headers.
    Must be associated with at least one of: contact, company, or deal.
    The email will be assigned to the current user.
    """
    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    owner_id = await shared_utils.get_current_hubspot_user_id(context)
    epoch = int(shared_utils.to_epoch_millis(when_occurred))

    to_emails = [
        {
            "email": to_email,
            "firstName": to_first_name or "",
            "lastName": to_last_name or "",
        }
    ]

    cc_email_list = None
    if cc_emails:
        cc_email_list = [{"email": email, "firstName": "", "lastName": ""} for email in cc_emails]

    bcc_email_list = None
    if bcc_emails:
        bcc_email_list = [{"email": email, "firstName": "", "lastName": ""} for email in bcc_emails]

    resp = await http_client.create_email(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        direction=direction.value if direction else "EMAIL",
        status=status.value if status else None,
        owner_id=str(owner_id),
        timestamp=epoch,
        from_email=from_email,
        from_first_name=from_first_name,
        from_last_name=from_last_name,
        to_emails=to_emails,
        cc_emails=cc_email_list,
        bcc_emails=bcc_email_list,
        contact_ids=[str(associate_to_contact_id)] if associate_to_contact_id else None,
        company_ids=[str(associate_to_company_id)] if associate_to_company_id else None,
        deal_ids=[str(associate_to_deal_id)] if associate_to_deal_id else None,
    )
    result = activities_helper.create_email_response(resp)
    return result


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",
            "crm.objects.contacts.write",
        ],
    ),
)
async def update_email_activity(
    context: ToolContext,
    email_id: Annotated[int | None, "The email activity ID to update."] = None,
    keywords: Annotated[
        str | None,
        "Keywords to search for email subjects or body text. Provide when email_id is not known.",
    ] = None,
    subject: Annotated[str | None, "Updated email subject."] = None,
    direction: Annotated[HubspotEmailDirection | None, "Updated email direction."] = None,
    status: Annotated[HubspotEmailStatus | None, "Updated email status."] = None,
    body_text: Annotated[str | None, "Updated plain-text body."] = None,
    body_html: Annotated[str | None, "Updated HTML body."] = None,
    when_occurred: Annotated[
        str | None,
        "Updated email timestamp (ISO format: YYYY-MM-DDTHH:MM:SS).",
    ] = None,
    matches_limit: Annotated[
        int,
        (
            "Maximum number of emails to return when searching by keywords. "
            "Defaults to 5. Max is 20."
        ),
    ] = 5,
) -> Annotated[
    UpdateEmailActivityResponse,
    "Update an email activity by ID or list matching emails when searching by keywords.",
]:
    """Update an email activity directly by ID or surface matches when searching by keywords."""
    shared_utils.ensure_single_identifier(
        entity_name="email_activity", identifier=email_id, keywords=keywords
    )

    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    if keywords is not None:
        capped_limit = shared_utils.cap_results_limit(
            requested_limit=matches_limit,
            default_limit=5,
            max_limit=20,
        )
        matches = await activities_helper.find_activities_by_keywords(
            http_client=http_client,
            activity_object=HubspotObject.EMAIL,
            keywords=keywords,
            limit=capped_limit,
        )

        summaries = activities_helper.summarize_activity_matches(
            activity_object=HubspotObject.EMAIL,
            matches=matches,
        )
        return cast(
            UpdateEmailActivityResponse,
            shared_utils.build_keyword_confirmation_response(
                entity_name="email_activity",
                keywords=keywords,
                matches=summaries,
                limit=capped_limit,
            ),
        )

    normalized_direction = (
        direction.value if isinstance(direction, HubspotEmailDirection) else direction
    )
    normalized_status = status.value if isinstance(status, HubspotEmailStatus) else status

    properties = activities_helper.build_email_update_properties(
        subject=subject,
        direction=normalized_direction,
        status=normalized_status,
        body_text=body_text,
        body_html=body_html,
        when_occurred=when_occurred,
    )

    updated = await activities_helper.update_activity_record(
        http_client=http_client,
        activity_object=HubspotObject.EMAIL,
        activity_id=str(email_id),
        properties=properties,
    )

    return cast(UpdateEmailActivityResponse, activities_helper.create_email_response(updated))


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.write",  # Write access for CRM objects including activities
        ],
    ),
)
async def create_meeting_activity(
    context: ToolContext,
    title: Annotated[str, "Meeting title."],
    start_date: Annotated[str, "Start date (YYYY-MM-DD format)."],
    start_time: Annotated[str, "Start time (HH:MM or HH:MM:SS format)."],
    duration: Annotated[
        str | None,
        "Meeting duration in HH:MM format (e.g., 1:30 for 1 hour 30 minutes).",
    ] = None,
    location: Annotated[str | None, "Meeting location."] = None,
    outcome: Annotated[
        HubspotMeetingOutcome | None,
        "Meeting outcome.",
    ] = None,
    associate_to_contact_id: Annotated[
        int | None,
        "Contact ID to associate this meeting with.",
    ] = None,
    associate_to_company_id: Annotated[
        int | None,
        "Company ID to associate this meeting with.",
    ] = None,
    associate_to_deal_id: Annotated[
        int | None,
        "Deal ID to associate this meeting with.",
    ] = None,
) -> Annotated[
    CreateMeetingActivityResponse,
    "Details of the meeting engagement activity created.",
]:
    """
    Create a meeting with essential fields including separate date and time.

    The start_date and start_time are combined to create the meeting timestamp.
    Duration can be specified in HH:MM format.
    Must be associated with at least one of: contact, company, or deal.
    The meeting will be assigned to the current user.
    """
    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    owner_id = await shared_utils.get_current_hubspot_user_id(context)

    resp = await http_client.create_meeting(
        title=title,
        start_date=start_date,
        start_time=start_time,
        duration=duration,
        location=location,
        outcome=outcome.value if outcome else None,
        owner_id=str(owner_id),
        contact_ids=[str(associate_to_contact_id)] if associate_to_contact_id else None,
        company_ids=[str(associate_to_company_id)] if associate_to_company_id else None,
        deal_ids=[str(associate_to_deal_id)] if associate_to_deal_id else None,
    )
    result = activities_helper.create_meeting_response(resp)
    return result


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",
            "crm.objects.contacts.write",
        ],
    ),
)
async def update_meeting_activity(
    context: ToolContext,
    meeting_id: Annotated[int | None, "The meeting activity ID to update."] = None,
    keywords: Annotated[
        str | None,
        "Keywords to search for meeting titles. Provide when meeting_id is not known.",
    ] = None,
    title: Annotated[str | None, "Updated meeting title."] = None,
    start_date: Annotated[str | None, "Updated start date (YYYY-MM-DD)."] = None,
    start_time: Annotated[str | None, "Updated start time (HH:MM or HH:MM:SS)."] = None,
    duration: Annotated[str | None, "Updated duration in HH:MM format."] = None,
    location: Annotated[str | None, "Updated meeting location."] = None,
    outcome: Annotated[HubspotMeetingOutcome | None, "Updated meeting outcome."] = None,
    matches_limit: Annotated[
        int,
        (
            "Maximum number of meetings to return when searching by keywords. "
            "Defaults to 5. Max is 20."
        ),
    ] = 5,
) -> Annotated[
    UpdateMeetingActivityResponse,
    "Update a meeting activity by ID or list matching meetings when searching by keywords.",
]:
    """Update a meeting activity directly by ID or surface matches when searching by keywords."""
    shared_utils.ensure_single_identifier(
        entity_name="meeting_activity", identifier=meeting_id, keywords=keywords
    )

    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    if keywords is not None:
        capped_limit = shared_utils.cap_results_limit(
            requested_limit=matches_limit,
            default_limit=5,
            max_limit=20,
        )
        matches = await activities_helper.find_activities_by_keywords(
            http_client=http_client,
            activity_object=HubspotObject.MEETING,
            keywords=keywords,
            limit=capped_limit,
        )

        summaries = activities_helper.summarize_activity_matches(
            activity_object=HubspotObject.MEETING,
            matches=matches,
        )
        return cast(
            UpdateMeetingActivityResponse,
            shared_utils.build_keyword_confirmation_response(
                entity_name="meeting_activity",
                keywords=keywords,
                matches=summaries,
                limit=capped_limit,
            ),
        )

    normalized_outcome = outcome.value if isinstance(outcome, HubspotMeetingOutcome) else outcome

    properties = activities_helper.build_meeting_update_properties(
        title=title,
        start_date=start_date,
        start_time=start_time,
        duration=duration,
        location=location,
        outcome=normalized_outcome,
    )

    updated = await activities_helper.update_activity_record(
        http_client=http_client,
        activity_object=HubspotObject.MEETING,
        activity_id=str(meeting_id),
        properties=properties,
    )

    return cast(UpdateMeetingActivityResponse, activities_helper.create_meeting_response(updated))


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.write",  # Write access for CRM objects including activities
        ],
    ),
)
async def create_communication_activity(
    context: ToolContext,
    channel: Annotated[
        HubspotCommunicationChannel,
        "Communication channel type.",
    ],
    when_occurred: Annotated[
        str,
        "When the communication occurred (ISO date format: YYYY-MM-DDTHH:MM:SS).",
    ],
    body_text: Annotated[str | None, "Full message content."] = None,
    associate_to_contact_id: Annotated[
        int | None,
        "Contact ID to associate this communication with.",
    ] = None,
    associate_to_company_id: Annotated[
        int | None,
        "Company ID to associate this communication with.",
    ] = None,
    associate_to_deal_id: Annotated[
        int | None,
        "Deal ID to associate this communication with.",
    ] = None,
) -> Annotated[
    CreateCommunicationActivityResponse,
    "Details of the communication engagement activity created.",
]:
    """
    Create a communication activity for logging communications that are not done via
    email, call, or meeting.

    This includes SMS, WhatsApp, LinkedIn messages, physical mail, and custom channel
    conversations.
    Must be associated with at least one of: contact, company, or deal.
    The communication will be assigned to the current user.
    """
    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    owner_id = await shared_utils.get_current_hubspot_user_id(context)
    epoch = int(shared_utils.to_epoch_millis(when_occurred))
    resp = await http_client.create_communication(
        channel=channel.value,
        logged_from="CRM",  # Default to CRM
        body_text=body_text,
        owner_id=str(owner_id),
        timestamp=epoch,
        contact_ids=[str(associate_to_contact_id)] if associate_to_contact_id else None,
        company_ids=[str(associate_to_company_id)] if associate_to_company_id else None,
        deal_ids=[str(associate_to_deal_id)] if associate_to_deal_id else None,
    )
    result = activities_helper.create_communication_response(resp)
    return result


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.read",
            "crm.objects.contacts.write",
        ],
    ),
)
async def update_communication_activity(
    context: ToolContext,
    communication_id: Annotated[int | None, "The communication activity ID to update."] = None,
    keywords: Annotated[
        str | None,
        (
            "Keywords to search for communication body text. Provide when "
            "communication_id is not known."
        ),
    ] = None,
    channel: Annotated[HubspotCommunicationChannel | None, "Updated communication channel."] = None,
    body_text: Annotated[str | None, "Updated message body."] = None,
    when_occurred: Annotated[
        str | None,
        "Updated timestamp (ISO format: YYYY-MM-DDTHH:MM:SS).",
    ] = None,
    matches_limit: Annotated[
        int,
        (
            "Maximum number of communications to return when searching by keywords. "
            "Defaults to 5. Max is 20."
        ),
    ] = 5,
) -> Annotated[
    UpdateCommunicationActivityResponse,
    (
        "Update a communication activity by ID or list matching communications "
        "when searching by keywords."
    ),
]:
    """Update a communication activity by ID or return matches for keyword searches."""
    shared_utils.ensure_single_identifier(
        entity_name="communication_activity",
        identifier=communication_id,
        keywords=keywords,
    )

    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    if keywords is not None:
        capped_limit = shared_utils.cap_results_limit(
            requested_limit=matches_limit,
            default_limit=5,
            max_limit=20,
        )
        matches = await activities_helper.find_activities_by_keywords(
            http_client=http_client,
            activity_object=HubspotObject.COMMUNICATION,
            keywords=keywords,
            limit=capped_limit,
        )

        summaries = activities_helper.summarize_activity_matches(
            activity_object=HubspotObject.COMMUNICATION,
            matches=matches,
        )
        return cast(
            UpdateCommunicationActivityResponse,
            shared_utils.build_keyword_confirmation_response(
                entity_name="communication_activity",
                keywords=keywords,
                matches=summaries,
                limit=capped_limit,
            ),
        )

    normalized_channel = (
        channel.value if isinstance(channel, HubspotCommunicationChannel) else channel
    )

    properties = activities_helper.build_communication_update_properties(
        channel=normalized_channel,
        body_text=body_text,
        when_occurred=when_occurred,
    )

    updated = await activities_helper.update_activity_record(
        http_client=http_client,
        activity_object=HubspotObject.COMMUNICATION,
        activity_id=str(communication_id),
        properties=properties,
    )

    return cast(
        UpdateCommunicationActivityResponse,
        activities_helper.create_communication_response(updated),
    )


@tool(
    requires_auth=Hubspot(
        scopes=[
            "oauth",
            "crm.objects.contacts.write",  # Write access for CRM objects including activities
            "crm.objects.deals.write",  # Allow associating to deals
        ],
    ),
)
async def associate_activity_to_deal(
    context: ToolContext,
    activity_type: Annotated[
        HubspotActivityType,
        "Engagement activity type.",
    ],
    activity_id: Annotated[int, "The activity object ID"],
    deal_id: Annotated[int, "The deal ID to associate to"],
) -> Annotated[dict[str, Any], "Associate an activity to a deal"]:
    """Associate a single activity object to a deal using HubSpot standard association type."""
    from arcade_hubspot.enums import HubspotAssociationType

    auth_token = shared_utils.get_auth_token_or_raise(context)
    http_client = HubspotHttpClient(auth_token=auth_token)

    activity_obj = activities_helper.activity_type_to_object(activity_type)

    resp = await http_client.create_association(
        from_object=activity_obj,
        from_id=str(activity_id),
        to_object=HubspotObject.DEAL,
        to_id=str(deal_id),
        association_type_id=str(HubspotAssociationType.ENGAGEMENT_TO_DEAL.value),
    )
    return resp if isinstance(resp, dict) else {"result": resp}
