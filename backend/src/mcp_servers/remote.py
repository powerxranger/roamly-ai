"""
Remote MCP servers, reached over HTTP.

Currently: Tavily (hotel / general web search).
"""

from src.mcp_servers.config import load_tools, require_tools

SERVER_NAME = "tavily"
SEARCH_TOOL_NAME = "tavily_search"


_search_tool = None


async def _get_search_tool():
    """Connect to Tavily once and keep the search tool handle."""

    global _search_tool

    if _search_tool is not None:
        return _search_tool

    tools = await load_tools(SERVER_NAME)
    require_tools(SERVER_NAME, tools, SEARCH_TOOL_NAME)

    _search_tool = tools[SEARCH_TOOL_NAME]

    return _search_tool


async def tavily_mcp_search(query: str):
    """Search the web via Tavily MCP."""

    tool = await _get_search_tool()

    return await tool.ainvoke({"query": query})
