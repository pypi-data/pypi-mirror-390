from collections.abc import Sequence
import functools
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from aiden_gsuite.credential import CREDENTIAL_ARG

class ToolHandler:
    def __init__(self, tool_name: str):
        self.name = tool_name

    # we ingest this information into every tool that requires a specified __credential__.
    # we also add what information actually can be used (account info). This way Claude
    # will know what to do.
    def get_supported_emails_tool_text(self) -> str:
        return f"""This tool requires a authorized Google account email for {CREDENTIAL_ARG} argument. You can choose one of: {", ".join(self.get_account_descriptions())}"""

    def get_tool_description(self) -> Tool:
        raise NotImplementedError()

    def run_tool(
        self, args: dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        raise NotImplementedError()


def handle_exceptions():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"An error occurred in {func.__name__}: {e}")
                return [TextContent(type="text", text=f"An error occurred: {e}")]
        return wrapper
    return decorator