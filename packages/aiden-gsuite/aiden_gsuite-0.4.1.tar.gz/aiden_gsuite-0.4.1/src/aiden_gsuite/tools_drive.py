import json
from collections.abc import Sequence
import logging

from mcp.types import (
    EmbeddedResource,
    ImageContent,
    TextContent,
    Tool,
)

from . import drive, toolhandler
from .credential import Credential

class SearchFilesToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("search_drive_files")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Searches for files in the user's google drive. 
                          You can search by file name or content. Simple text searches will be converted to proper query format.
                          Examples: "document", "report.pdf", "name contains 'meeting'", "fullText contains 'budget'"
                          Returns a list of file ids and names.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for files.",
                    },
                    "page_size": {
                        "type": "number",
                        "description": "The number of files to return.",
                        "default": 100,
                    },
                    "search_name": {
                        "type": "boolean",
                        "description": "Whether to search by file name.",
                        "default": True,
                    },
                    "search_content": {
                        "type": "boolean",
                        "description": "Whether to search by file content.",
                        "default": True,
                    },
                },
                "required": ["query"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        drive_service = drive.DriveService(Credential(args))
        query = args["query"].replace("'", "\\'")

        search_name = args.get("search_name", True)
        search_content = args.get("search_content", True)

        if search_name and search_content:
            query = f"fullText contains '{query}' or name contains '{query}'"
        elif search_name:
            query = f"name contains '{query}'"
        elif search_content:
            query = f"fullText contains '{query}'"

        logging.info(f"Search files query: {query}")

        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"files": drive_service.search_files(query)}, indent=2
                ),
            )
        ]


class CreateFolderToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("create_drive_folder")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Creates a folder in the user's drive.
                          Returns a folder id and name.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {
                        "type": "string",
                        "description": "The name of the folder to create.",
                    },
                    "parent_folder_id": {
                        "type": "string",
                        "description": "The id of the parent folder to create the folder in.",
                        "default": "root",
                    },
                },
                "required": ["folder_name"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        drive_service = drive.DriveService(Credential(args))
        parent_folder_id = args.get("parent_folder_id", "root")
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "folder_id": drive_service.create_folder(args["folder_name"], parent_folder_id),
                    },
                    indent=2,
                ),
            )
        ]


class CreateFileToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("create_drive_file")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Creates a file in the user's google drive.
                          Returns a file id and name.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "The name of the file to create.",
                    },
                    "folder_id": {
                        "type": "string",
                        "description": "The id of the folder to create the file in.",
                        "default": "root",
                    },
                },
                "required": ["file_name"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        drive_service = drive.DriveService(Credential(args))
        folder_id = args.get("folder_id", "root")
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "file_id": drive_service.create_file(args["file_name"], folder_id),
                    },
                    indent=2,
                )
            )
        ]


class ListFilesToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("list_drive_files")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Lists all files in a google drive folder.
                          Returns a list of file ids and names.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_id": {
                        "type": "string",
                        "description": "The id (not name) of the folder to list files from.",
                        "default": "root",
                    }
                },
                "required": [],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        drive_service = drive.DriveService(Credential(args))
        folder_id = args.get("folder_id", "root")
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "files": drive_service.list_files(folder_id),
                }, indent=2),
            )
        ]

class ReadFileToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("read_drive_file")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Reads a google drive file by its id.
                          Returns the file content.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "The id of the file to read.",
                    }
                },
                "required": ["file_id"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        drive_service = drive.DriveService(Credential(args))
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "file_content": drive_service.read_file(args["file_id"]),
                }, indent=2),
            )
        ]
    
class TrashFileOrFolderToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("trash_drive_file_or_folder")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Trashes a google drive file or folder by its id.
                          Returns a success message.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "The id of the file or folder to trash.",
                    }
                },
                "required": ["file_id"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        drive_service = drive.DriveService(Credential(args))
        drive_service.trash_file_or_folder(args["file_id"])
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "message": "File or folder trashed successfully.",
                }, indent=2),
            )
        ]
    
class RestoreFileOrFolderToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("restore_drive_file_or_folder")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Restores a google drive file or folder by its id.
                          Returns a success message.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "The id of the file or folder to restore.",
                    }
                },
                "required": ["file_id"],
            },
        )

    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        drive_service = drive.DriveService(Credential(args))
        drive_service.restore_file_or_folder(args["file_id"])
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "message": "File or folder restored successfully.",
                }, indent=2),
            )
        ]
    
class EmptyTrashToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("empty_drive_trash")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Empties the trash in the user's google drive.
                          Returns a success message.""",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        )
    
    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        drive_service = drive.DriveService(Credential(args))
        drive_service.empty_trash()
        return [
            TextContent(
                type="text",
                text=json.dumps({   
                    "message": "Trash emptied successfully.",
                }, indent=2),
            )
        ]
    
class ListTrashToolHandler(toolhandler.ToolHandler):
    def __init__(self):
        super().__init__("list_drive_trash")

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description="""Lists all files in the trash in the user's google drive.
                          Returns a list of file ids and names.""",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        )
    
    @toolhandler.handle_exceptions()
    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        drive_service = drive.DriveService(Credential(args))
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "files": drive_service.list_trash(),
                }, indent=2),
            )
        ]