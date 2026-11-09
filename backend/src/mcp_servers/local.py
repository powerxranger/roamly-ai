"""
Local MCP servers, spawned as stdio child processes.

* weather - our own server in this package (weather_server.py)
"""

from src.mcp_servers.config import (
    WEATHER_SERVER_PATH,
    load_tools,
    require_tools,
)

WEATHER_SERVER_NAME = "weather"

CURRENT_WEATHER_TOOL = "get_current_weather"
FORECAST_TOOL = "get_forecast"


# =========================
# Weather
# =========================

_weather_tools: dict = {}


async def _get_weather_tools() -> dict:
    global _weather_tools

    if _weather_tools:
        return _weather_tools

    if not WEATHER_SERVER_PATH.exists():
        raise FileNotFoundError(
            f"Weather MCP server file was not found: {WEATHER_SERVER_PATH}"
        )

    tools = await load_tools(WEATHER_SERVER_NAME)

    require_tools(
        WEATHER_SERVER_NAME,
        tools,
        CURRENT_WEATHER_TOOL,
        FORECAST_TOOL,
    )

    _weather_tools = tools

    return _weather_tools


async def weather_mcp_search(city: str):
    """Current conditions for the given city."""
    tools = await _get_weather_tools()
    return await tools[CURRENT_WEATHER_TOOL].ainvoke({"city": city})


async def forecast_mcp_search(city: str):
    """Multi-day forecast for the given city."""
    tools = await _get_weather_tools()
    return await tools[FORECAST_TOOL].ainvoke({"city": city})
