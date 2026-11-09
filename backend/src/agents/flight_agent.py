"""Turns the user query into concrete flight guidance using live web search."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import (
    FLIGHT_AGENT_PROMPT,
    FLIGHT_SEARCH_QUERY,
    FLIGHT_SYSTEM_PROMPT,
)
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.mcp_servers.remote import tavily_mcp_search
from src.utils.async_utils import bump_llm_calls, run_async, truncate


def flight_agent(state: TravelState):
    print("\nINSIDE FLIGHT AGENT\n")

    query = state["user_query"]

    try:
        search_query = FLIGHT_SEARCH_QUERY.format(user_query=query)
        flight_search_results = run_async(tavily_mcp_search(search_query))

        prompt = FLIGHT_AGENT_PROMPT.format(
            query=query,
            flight_data=truncate(flight_search_results, 1500),
        )

        response = get_llm().invoke([
            SystemMessage(content=FLIGHT_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        flight_data = response.content

    except Exception as e:
        flight_data = f"Flight information unavailable: {str(e)}"

    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content="Flight recommendations generated")
        ],
        "llm_calls": bump_llm_calls(state),
    }
