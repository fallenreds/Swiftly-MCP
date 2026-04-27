# Swiftly MCP Server

FastMCP server for [Swiftly](https://swiftly.cc) — a meeting recording, transcription and AI summary platform.

## Tools

| Category | Tools |
|---|---|
| **Auth / User** | `validate_token`, `get_me`, `change_name`, `change_ai_language`, `change_transcription_language`, `get_available_languages` |
| **Meetings** | `list_meetings`, `get_meeting`, `create_meeting`, `update_meeting`, `delete_meeting`, `delete_all_meetings` |
| **Groups** | `list_groups`, `get_group`, `create_group`, `update_group`, `delete_group`, `add_meeting_to_group`, `remove_meeting_from_group` |
| **Notes** | `get_note`, `create_note`, `update_note`, `delete_note` |
| **Transcriptions** | `list_transcriptions`, `download_transcriptions`, `create_ai_summary`, `edit_ai_transcription`, `list_ai_transcriptions`, `get_ai_transcription`, `delete_ai_transcription` |
| **Prompts** | `get_prompt`, `create_prompt`, `update_prompt`, `delete_prompt` |
| **Speakers** | `list_speakers`, `get_speaker` |
| **Bot** | `start_bot`, `stop_bot`, `get_bot_status`, `list_bot_sessions` |
| **Calendar** | `get_calendar_status`, `get_calendar_events`, `sync_calendar` |
| **Jira** | `get_jira_user`, `list_jira_tasks`, `disconnect_jira` |
| **Confluence** | `list_confluence_pages`, `get_confluence_me` |
| **Asana** | `get_asana_user`, `list_asana_tasks`, `disconnect_asana` |
| **Google Docs** | `list_google_docs`, `get_google_doc_content`, `list_available_google_docs` |
| **Health** | `health_check` |

## Authentication

All tools accept an `auth_token` parameter (your Swiftly Bearer token).  
Get your token from `https://swiftly.cc` after Google OAuth login.

The token can also be provided via `SWIFTLY_TOKEN` env variable (see below).

## Setup

### Install

```bash
pip install fastmcp httpx
```

### Run as stdio (Claude Desktop)

```bash
python server.py
```

### Claude Desktop config (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "swiftly": {
      "command": "python",
      "args": ["/absolute/path/to/swiftly-mcp/server.py"],
      "env": {
        "SWIFTLY_BASE_URL": "https://swiftly.cc"
      }
    }
  }
}
```

### Run as HTTP server (for remote access / Claude.ai connector)

```bash
fastmcp run server.py --transport streamable-http --port 8000
```

Then register `http://localhost:8000/mcp` as a custom MCP connector in Claude.ai settings.

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `SWIFTLY_BASE_URL` | `https://swiftly.cc` | Swiftly API base URL |

## Notes

- Every tool call requires a valid `auth_token`. Obtain it via Swiftly's Google OAuth flow at `https://swiftly.cc/api/v1/auth/google`.
- `delete_all_meetings` is destructive — it deletes every meeting and transcript for the user.
- Bot tools (`start_bot`, `stop_bot`) control the Swiftly recording bot that joins Google Meet / Zoom / Teams calls.
