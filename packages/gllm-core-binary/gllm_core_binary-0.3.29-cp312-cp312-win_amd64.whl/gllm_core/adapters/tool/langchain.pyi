from gllm_core.schema.tool import Tool as Tool
from typing import Any

def from_langchain_tool(langchain_tool: Any) -> Tool:
    """Convert a LangChain tool into the SDK Tool representation.

    Args:
        langchain_tool (Any): The LangChain tool to convert.

    Returns:
        Tool: The converted SDK tool.

    Raises:
        ValueError: If the input is not a valid LangChain tool.
    """
