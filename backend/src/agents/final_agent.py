"""Formats everything the other agents produced into the user-facing executive synthesis."""

import time
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.prompts import FINAL_AGENT_PROMPT, FINAL_SYSTEM_PROMPT
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.utils.async_utils import bump_llm_calls, truncate


def final_agent(state: TravelState):
    # Short pause to allow Groq rate-limiting token bucket to replenish
    time.sleep(1.5)

    prompt = FINAL_AGENT_PROMPT.format(
        user_query=state["user_query"],
        flight_results=truncate(state.get("flight_results", ""), 500),
        hotel_results=truncate(state.get("hotel_results", ""), 500),
        weather_results=truncate(state.get("weather_results", ""), 300),
        itinerary=truncate(state.get("itinerary", ""), 600),
    )

    response = get_llm().invoke([
        SystemMessage(content=FINAL_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    return {
        "messages": [response],
        "llm_calls": bump_llm_calls(state),
    }
