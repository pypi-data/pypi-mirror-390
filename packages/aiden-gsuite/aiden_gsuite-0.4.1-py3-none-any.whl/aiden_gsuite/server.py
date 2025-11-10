import logging
import os
import traceback
from collections.abc import Sequence
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import (
    EmbeddedResource,
    ImageContent,
    TextContent,
    Tool,
)

from aiden_gsuite import tools_drive, tools_map

from . import toolhandler, tools_calendar, tools_gmail

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-gsuite")

app = Server("mcp-gsuite")

tool_handlers = {}


def add_tool_handler(tool_class: toolhandler.ToolHandler):
    global tool_handlers

    tool_handlers[tool_class.name] = tool_class


def get_tool_handler(name: str) -> toolhandler.ToolHandler | None:
    if name not in tool_handlers:
        return None

    return tool_handlers[name]


add_tool_handler(tools_gmail.QueryEmailsToolHandler())
add_tool_handler(tools_gmail.GetEmailByIdToolHandler())
add_tool_handler(tools_gmail.CreateDraftToolHandler())
add_tool_handler(tools_gmail.SendDraftToolHandler())
add_tool_handler(tools_gmail.DeleteDraftToolHandler())
add_tool_handler(tools_gmail.DeleteEmailToolHandler())
add_tool_handler(tools_gmail.ReplyEmailToolHandler())
add_tool_handler(tools_gmail.GetAttachmentToolHandler())
add_tool_handler(tools_gmail.BulkGetEmailsByIdsToolHandler())
add_tool_handler(tools_gmail.BulkSaveAttachmentsToolHandler())

add_tool_handler(tools_calendar.ListCalendarsToolHandler())
add_tool_handler(tools_calendar.GetCalendarEventsToolHandler())
add_tool_handler(tools_calendar.CreateCalendarEventToolHandler())
add_tool_handler(tools_calendar.ModifyCalendarEventToolHandler())
add_tool_handler(tools_calendar.DeleteCalendarEventToolHandler())

add_tool_handler(tools_drive.SearchFilesToolHandler())
add_tool_handler(tools_drive.CreateFolderToolHandler())
add_tool_handler(tools_drive.CreateFileToolHandler())
add_tool_handler(tools_drive.ListFilesToolHandler())
add_tool_handler(tools_drive.ReadFileToolHandler())
add_tool_handler(tools_drive.TrashFileOrFolderToolHandler())
add_tool_handler(tools_drive.RestoreFileOrFolderToolHandler())
add_tool_handler(tools_drive.EmptyTrashToolHandler())
add_tool_handler(tools_drive.ListTrashToolHandler())

# if GOOGLE_MAPS_API_KEY is set, add the tools_maps tool handler
if os.getenv("GOOGLE_MAPS_API_KEY"):
    add_tool_handler(tools_map.GeocodeToolHandler())
    add_tool_handler(tools_map.ReverseGeocodeToolHandler())
    add_tool_handler(tools_map.SearchPlacesToolHandler())
    add_tool_handler(tools_map.PlaceDetailsToolHandler())
    add_tool_handler(tools_map.DistanceMatrixToolHandler())
    add_tool_handler(tools_map.ElevationToolHandler())
    add_tool_handler(tools_map.DirectionsToolHandler())


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""

    return [th.get_tool_description() for th in tool_handlers.values()]


@app.call_tool()
async def call_tool(
    name: str, arguments: Any
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    try:
        if not isinstance(arguments, dict):
            raise RuntimeError("arguments must be dictionary")

        tool_handler = get_tool_handler(name)
        if not tool_handler:
            raise ValueError(f"Unknown tool: {name}")

        return tool_handler.run_tool(arguments)
    except Exception as e:
        logging.error(traceback.format_exc())
        logging.error(f"Error during call_tool: {str(e)}")
        raise RuntimeError(f"Caught Exception. Error: {str(e)}")


async def main():
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
