"""Fetches current weather and forecast for the extracted destination."""

from langchain_core.messages import AIMessage

from src.agents.destination import extract_destination
from src.agents.prompts import WEATHER_RESULTS_TEMPLATE
from src.graph.state import TravelState
from src.mcp_servers.local import forecast_mcp_search, weather_mcp_search
from src.utils.async_utils import bump_llm_calls, run_async, truncate


def weather_agent(state: TravelState):
    city = extract_destination(state["user_query"])

    weather_data = run_async(weather_mcp_search(city))
    forecast_data = run_async(forecast_mcp_search(city))

    formatted_weather = WEATHER_RESULTS_TEMPLATE.format(
        weather_data=truncate(weather_data, 400),
        forecast_data=truncate(forecast_data, 400),
    )

    return {
        "weather_results": formatted_weather,
        "messages": [
            AIMessage(content="Weather information fetched")
        ],
        "llm_calls": bump_llm_calls(),
    }
