"""Combines flight, hotel and weather results into a day-by-day itinerary."""

import time
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.prompts import ITINERARY_AGENT_PROMPT, ITINERARY_SYSTEM_PROMPT
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.utils.async_utils import bump_llm_calls, truncate


def itinerary_agent(state: TravelState):
    # Short pause to allow Groq rate-limiting token bucket to replenish after parallel fan-out
    time.sleep(1.5)

    prompt = ITINERARY_AGENT_PROMPT.format(
        user_query=state["user_query"],
        flight_results=truncate(state.get("flight_results", ""), 800),
        hotel_results=truncate(state.get("hotel_results", ""), 800),
        weather_results=truncate(state.get("weather_results", ""), 400),
    )

    response = get_llm().invoke([
        SystemMessage(content=ITINERARY_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": bump_llm_calls(state),
    }
