"""
Swiftly MCP Server
==================
FastMCP server for the Swiftly API (https://swiftly.cc/api/v1/...)
Authentication: Bearer token passed via Authorization header.
"""

import os
import httpx
from typing import Optional
from fastmcp import FastMCP

BASE_URL = os.getenv("SWIFTLY_BASE_URL", "https://swiftly.cc")

mcp = FastMCP(
    name="Swiftly",
    instructions=(
        "Use this server to interact with Swiftly — a meeting recording and transcription platform. "
        "You can manage meetings, notes, transcriptions, AI summaries, speakers, bot sessions, "
        "calendar integrations, and integrations with Jira, Confluence, Asana, and Google Docs. "
        "All tools require a valid Bearer token passed as `auth_token`."
    ),
)


def _headers(auth_token: str) -> dict:
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }


def _get(auth_token: str, path: str, params: dict | None = None) -> dict:
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        resp = client.get(path, headers=_headers(auth_token), params={k: v for k, v in (params or {}).items() if v is not None})
        resp.raise_for_status()
        return resp.json()


def _post(auth_token: str, path: str, body: dict | None = None, params: dict | None = None) -> dict:
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        resp = client.post(path, headers=_headers(auth_token), json=body, params={k: v for k, v in (params or {}).items() if v is not None})
        resp.raise_for_status()
        return resp.json()


def _patch(auth_token: str, path: str, body: dict) -> dict:
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        resp = client.patch(path, headers=_headers(auth_token), json=body)
        resp.raise_for_status()
        return resp.json()


def _delete(auth_token: str, path: str, params: dict | None = None, body: dict | None = None) -> dict:
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        resp = client.request("DELETE", path, headers=_headers(auth_token),
                              params={k: v for k, v in (params or {}).items() if v is not None},
                              json=body)
        resp.raise_for_status()
        try:
            return resp.json()
        except Exception:
            return {"status": resp.status_code}


# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────

@mcp.tool()
def validate_token(auth_token: str) -> dict:
    """Validate a Swiftly Bearer token. Returns the token status."""
    return _post(auth_token, "/api/v1/auth/validate-token")


@mcp.tool()
def get_me(auth_token: str) -> dict:
    """Get the current authenticated user's profile."""
    return _get(auth_token, "/api/v1/users/me")


# ─────────────────────────────────────────────
# MEETINGS
# ─────────────────────────────────────────────

@mcp.tool()
def list_meetings(
    auth_token: str,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    ordering: Optional[str] = None,
    group_ids: Optional[str] = None,
    created_at_gte: Optional[str] = None,
    created_at_lte: Optional[str] = None,
    started_at_gte: Optional[str] = None,
    started_at_lte: Optional[str] = None,
) -> dict:
    """
    List all meetings with optional filtering and pagination.
    - group_ids: comma-separated group IDs to filter by
    - ordering: e.g. '-created_at', 'started_at'
    - *_gte / *_lte: ISO datetime strings for date range filters
    """
    return _get(auth_token, "/api/v1/meetings", {
        "page": page, "page_size": page_size, "search": search,
        "ordering": ordering, "group_ids": group_ids,
        "created_at_gte": created_at_gte, "created_at_lte": created_at_lte,
        "started_at_gte": started_at_gte, "started_at_lte": started_at_lte,
    })


@mcp.tool()
def get_meeting(auth_token: str, meeting_id: int) -> dict:
    """Get a single meeting by ID."""
    return _get(auth_token, "/api/v1/meeting/get", {"meeting_id": meeting_id})


@mcp.tool()
def create_meeting(
    auth_token: str,
    google_meeting_id: str,
    meeting_title: Optional[str],
    start_time: int,
) -> dict:
    """
    Create a new meeting record.
    - google_meeting_id: Google Meet room ID
    - start_time: Unix timestamp (seconds)
    """
    return _post(auth_token, "/api/v1/meeting/create", {
        "google_meeting_id": google_meeting_id,
        "meeting_title": meeting_title,
        "start_time": start_time,
    })


@mcp.tool()
def update_meeting(
    auth_token: str,
    meeting_id: int,
    meeting_title: Optional[str] = None,
) -> dict:
    """Update a meeting's title or metadata."""
    return _patch(auth_token, "/api/v1/meeting/update", {
        "meeting_id": meeting_id,
        "meeting_title": meeting_title,
    })


@mcp.tool()
def delete_meeting(auth_token: str, meeting_id: int) -> dict:
    """Delete a single meeting by ID."""
    return _delete(auth_token, "/api/v1/meeting/delete", {"meeting_id": meeting_id})


@mcp.tool()
def delete_all_meetings(auth_token: str) -> dict:
    """⚠️ Delete ALL meetings and transcriptions for the current user."""
    return _delete(auth_token, "/api/v1/meetings/delete/all")


# ─────────────────────────────────────────────
# MEETING GROUPS
# ─────────────────────────────────────────────

@mcp.tool()
def list_groups(
    auth_token: str,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    ordering: Optional[str] = None,
) -> dict:
    """List all meeting groups."""
    return _get(auth_token, "/api/v1/meetings/group", {
        "page": page, "page_size": page_size, "search": search, "ordering": ordering,
    })


@mcp.tool()
def get_group(auth_token: str, group_id: int) -> dict:
    """Get a single meeting group by ID."""
    return _get(auth_token, "/api/v1/meetings/group/get", {"group_id": group_id})


@mcp.tool()
def create_group(auth_token: str, name: str) -> dict:
    """Create a new meeting group."""
    return _post(auth_token, "/api/v1/meetings/group/create", {"name": name})


@mcp.tool()
def update_group(auth_token: str, group_id: int, name: str) -> dict:
    """Rename a meeting group."""
    return _patch(auth_token, "/api/v1/group/update", {"group_id": group_id, "name": name})


@mcp.tool()
def delete_group(auth_token: str, group_id: int) -> dict:
    """Delete a meeting group."""
    return _delete(auth_token, "/api/v1/meetings/group/delete", {"group_id": group_id})


@mcp.tool()
def add_meeting_to_group(auth_token: str, meeting_id: int, group_id: int) -> dict:
    """Add a meeting to a group."""
    return _post(auth_token, "/api/v1/meetings/group/add", {
        "meeting_id": meeting_id, "group_id": group_id,
    })


@mcp.tool()
def remove_meeting_from_group(auth_token: str, meeting_id: int, group_id: int) -> dict:
    """Remove a meeting from a group."""
    return _post(auth_token, "/api/v1/meetings/group/remove", {
        "meeting_id": meeting_id, "group_id": group_id,
    })


# ─────────────────────────────────────────────
# NOTES
# ─────────────────────────────────────────────

@mcp.tool()
def get_note(auth_token: str, meeting_id: int) -> dict:
    """Get the note for a meeting."""
    return _get(auth_token, "/api/v1/note", {"meeting_id": meeting_id})


@mcp.tool()
def create_note(auth_token: str, meeting_id: int, text: str) -> dict:
    """Create a note for a meeting."""
    return _post(auth_token, "/api/v1/note/create", {"meeting_id": meeting_id, "text": text})


@mcp.tool()
def update_note(auth_token: str, meeting_id: int, text: str) -> dict:
    """Update the note for a meeting."""
    return _patch(auth_token, "/api/v1/note/update", {"meeting_id": meeting_id, "text": text})


@mcp.tool()
def delete_note(auth_token: str, meeting_id: int) -> dict:
    """Delete the note for a meeting."""
    return _delete(auth_token, "/api/v1/note/delete", body={"meeting_id": meeting_id})


# ─────────────────────────────────────────────
# TRANSCRIPTIONS
# ─────────────────────────────────────────────

@mcp.tool()
def list_transcriptions(
    auth_token: str,
    meeting_id: int,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    """List transcription segments for a meeting."""
    return _get(auth_token, "/api/v1/transcriptions", {
        "meeting_id": meeting_id, "page": page, "page_size": page_size,
    })


@mcp.tool()
def download_transcriptions(
    auth_token: str,
    meeting_id: int,
    file_type: str = "txt",
) -> dict:
    """
    Download transcriptions for a meeting.
    - file_type: 'txt', 'docx', 'pdf', or 'srt'
    """
    return _get(auth_token, "/api/v1/transcriptions/download", {
        "meeting_id": meeting_id, "file_type": file_type,
    })


@mcp.tool()
def create_ai_summary(
    auth_token: str,
    meeting_id: int,
    prompt_id: Optional[int] = None,
) -> dict:
    """
    Run AI processing on a meeting transcription to generate a summary or structured output.
    Optionally provide a custom prompt_id.
    """
    body: dict = {"meeting_id": meeting_id}
    if prompt_id is not None:
        body["prompt_id"] = prompt_id
    return _post(auth_token, "/api/v1/transcriptions/ai", body)


@mcp.tool()
def edit_ai_transcription(
    auth_token: str,
    transcription_id: int,
    text: str,
) -> dict:
    """Edit an existing AI transcription result."""
    return _post(auth_token, "/api/v1/transcriptions/ai/edit", {
        "transcription_id": transcription_id,
        "text": text,
    })


@mcp.tool()
def list_ai_transcriptions(
    auth_token: str,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """List all AI-generated transcription summaries for the user."""
    return _get(auth_token, "/api/v1/ai/transcription/list", {
        "page": page, "page_size": page_size,
    })


@mcp.tool()
def get_ai_transcription(auth_token: str, transcription_id: int) -> dict:
    """Get a single AI transcription summary by ID."""
    return _get(auth_token, f"/api/v1/ai/transcription/{transcription_id}")


@mcp.tool()
def delete_ai_transcription(auth_token: str, transcription_id: int) -> dict:
    """Delete an AI transcription summary."""
    return _delete(auth_token, f"/api/v1/ai/transcription/{transcription_id}")


# ─────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────

@mcp.tool()
def get_prompt(auth_token: str, prompt_id: int) -> dict:
    """Get a custom AI prompt by ID."""
    return _get(auth_token, "/api/v1/prompt", {"prompt_id": prompt_id})


@mcp.tool()
def create_prompt(
    auth_token: str,
    name: str,
    text: str,
) -> dict:
    """Create a new custom AI prompt."""
    return _post(auth_token, "/api/v1/prompt", {"name": name, "text": text})


@mcp.tool()
def update_prompt(
    auth_token: str,
    prompt_id: int,
    name: Optional[str] = None,
    text: Optional[str] = None,
) -> dict:
    """Update an existing custom AI prompt."""
    return _patch(auth_token, "/api/v1/prompt", {
        "prompt_id": prompt_id, "name": name, "text": text,
    })


@mcp.tool()
def delete_prompt(auth_token: str, prompt_id: int) -> dict:
    """Delete a custom AI prompt."""
    return _delete(auth_token, "/api/v1/prompt", {"prompt_id": prompt_id})


# ─────────────────────────────────────────────
# SPEAKERS
# ─────────────────────────────────────────────

@mcp.tool()
def list_speakers(auth_token: str, meeting_id: int) -> dict:
    """List all speakers identified in a meeting."""
    return _get(auth_token, "/api/v1/speaker/get-list", {"meeting_id": meeting_id})


@mcp.tool()
def get_speaker(auth_token: str, meeting_id: int, speaker_id: int) -> dict:
    """Get details of a specific speaker in a meeting."""
    return _delete(auth_token, "/api/v1/speaker/get-one", {
        "meeting_id": meeting_id, "speaker_id": speaker_id,
    })


# ─────────────────────────────────────────────
# BOT
# ─────────────────────────────────────────────

@mcp.tool()
def start_bot(
    auth_token: str,
    meeting_url: str,
    bot_name: Optional[str] = None,
) -> dict:
    """
    Start a Swiftly recording bot in a meeting.
    - meeting_url: the Google Meet / Zoom / Teams URL
    - bot_name: display name for the bot in the meeting
    """
    body: dict = {"meeting_url": meeting_url}
    if bot_name:
        body["bot_name"] = bot_name
    return _post(auth_token, "/api/v1/bot/start", body)


@mcp.tool()
def stop_bot(auth_token: str, session_id: str) -> dict:
    """Stop an active bot session."""
    return _post(auth_token, f"/api/v1/bot/stop/{session_id}")


@mcp.tool()
def get_bot_status(auth_token: str, session_id: str) -> dict:
    """Get the current status of a bot session."""
    return _get(auth_token, f"/api/v1/bot/status/{session_id}")


@mcp.tool()
def list_bot_sessions(auth_token: str) -> dict:
    """List all bot sessions for the current user."""
    return _get(auth_token, "/api/v1/bot/sessions")


# ─────────────────────────────────────────────
# CALENDAR INTEGRATION
# ─────────────────────────────────────────────

@mcp.tool()
def get_calendar_status(auth_token: str, user_id: Optional[str] = None) -> dict:
    """Get the Google Calendar integration status."""
    return _get(auth_token, "/api/v1/integration/calendar/status", {"user_id": user_id})


@mcp.tool()
def get_calendar_events(
    auth_token: str,
    user_id: Optional[str] = None,
    days_ahead: int = 7,
) -> dict:
    """
    Get upcoming calendar events.
    - days_ahead: number of days to look ahead (default 7)
    """
    return _get(auth_token, "/api/v1/integration/calendar/events", {
        "user_id": user_id, "days_ahead": days_ahead,
    })


@mcp.tool()
def sync_calendar(auth_token: str) -> dict:
    """Trigger a manual calendar sync."""
    return _post(auth_token, "/api/v1/integration/calendar/sync")


# ─────────────────────────────────────────────
# JIRA INTEGRATION
# ─────────────────────────────────────────────

@mcp.tool()
def get_jira_user(auth_token: str) -> dict:
    """Get the connected Jira user info."""
    return _get(auth_token, "/api/v1/atlassian/jira/user")


@mcp.tool()
def list_jira_tasks(
    auth_token: str,
    meeting_id: int,
    limit: int = 20,
    offset: int = 0,
    search: Optional[str] = None,
) -> dict:
    """List Jira tasks linked to a meeting."""
    return _get(auth_token, "/api/v1/jira/tasks", {
        "meeting_id": meeting_id, "limit": limit, "offset": offset, "search": search,
    })


@mcp.tool()
def disconnect_jira(auth_token: str) -> dict:
    """Disconnect the Jira integration."""
    return _get(auth_token, "/api/v1/atlassian/jira/disconnect")


# ─────────────────────────────────────────────
# CONFLUENCE INTEGRATION
# ─────────────────────────────────────────────

@mcp.tool()
def list_confluence_pages(
    auth_token: str,
    meeting_id: int,
    space_id: Optional[str] = None,
    page_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    content_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    search: Optional[str] = None,
) -> dict:
    """List Confluence pages linked to a meeting."""
    return _get(auth_token, "/api/v1/confluence/pages", {
        "meeting_id": meeting_id, "spase_id": space_id, "page_id": page_id,
        "parent_id": parent_id, "content_type": content_type,
        "limit": limit, "offset": offset, "search": search,
    })


@mcp.tool()
def get_confluence_me(auth_token: str) -> dict:
    """Get the connected Confluence user info."""
    return _get(auth_token, "/api/v1/atlassian/confluence/me")


# ─────────────────────────────────────────────
# ASANA INTEGRATION
# ─────────────────────────────────────────────

@mcp.tool()
def get_asana_user(auth_token: str) -> dict:
    """Get the connected Asana user info."""
    return _get(auth_token, "/api/v1/asana/user")


@mcp.tool()
def list_asana_tasks(
    auth_token: str,
    meeting_id: int,
    limit: int = 20,
    offset: int = 0,
    search: Optional[str] = None,
) -> dict:
    """List Asana tasks linked to a meeting."""
    return _get(auth_token, "/api/v1/asana/tasks", {
        "meeting_id": meeting_id, "limit": limit, "offset": offset, "search": search,
    })


@mcp.tool()
def disconnect_asana(auth_token: str) -> dict:
    """Disconnect the Asana integration."""
    return _get(auth_token, "/api/v1/asana/disconnect")


# ─────────────────────────────────────────────
# GOOGLE DOCS INTEGRATION
# ─────────────────────────────────────────────

@mcp.tool()
def list_google_docs(
    auth_token: str,
    meeting_id: int,
    limit: int = 20,
    offset: int = 0,
    search: Optional[str] = None,
) -> dict:
    """List Google Docs linked to a meeting."""
    return _get(auth_token, "/api/v1/google-docs/list", {
        "meeting_id": meeting_id, "limit": limit, "offset": offset, "search": search,
    })


@mcp.tool()
def get_google_doc_content(auth_token: str, document_id: str) -> dict:
    """Get the content of a specific Google Doc."""
    return _get(auth_token, "/api/v1/google-docs/content", {"document_id": document_id})


@mcp.tool()
def list_available_google_docs(auth_token: str, meeting_id: int) -> dict:
    """List Google Docs already attached/available for a meeting."""
    return _get(auth_token, "/api/v1/google-docs/available", {"meeting_id": meeting_id})


# ─────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────

@mcp.tool()
def get_available_languages(auth_token: str) -> dict:
    """Get all available AI and transcription languages."""
    return _get(auth_token, "/api/v1/users/available-languages")


@mcp.tool()
def change_ai_language(auth_token: str, language: str) -> dict:
    """Change the AI output language for the current user."""
    return _post(auth_token, "/api/v1/users/change-ai-language", {"language": language})


@mcp.tool()
def change_transcription_language(auth_token: str, language: str) -> dict:
    """Change the transcription language for the current user."""
    return _post(auth_token, "/api/v1/users/change-transcription-language", {"language": language})


@mcp.tool()
def change_name(auth_token: str, name: str) -> dict:
    """Change the display name of the current user."""
    return _post(auth_token, "/api/v1/users/change-name", {"name": name})


# ─────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────

@mcp.tool()
def health_check(auth_token: str = "") -> dict:
    """Check if the Swiftly API is alive (no auth required)."""
    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        resp = client.get("/healthz")
        resp.raise_for_status()
        return resp.json()


if __name__ == "__main__":
    mcp.run()
