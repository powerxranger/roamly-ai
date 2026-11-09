"""Finds hotel options for the destination through the Tavily MCP server."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import (
    HOTEL_AGENT_PROMPT,
    HOTEL_SEARCH_QUERY,
    HOTEL_SYSTEM_PROMPT,
)
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.mcp_servers.remote import tavily_mcp_search
from src.utils.async_utils import bump_llm_calls, run_async, truncate


def hotel_agent(state: TravelState):
    query = state["user_query"]

    try:
        search_query = HOTEL_SEARCH_QUERY.format(user_query=query)
        hotel_search_results = run_async(tavily_mcp_search(search_query))

        prompt = HOTEL_AGENT_PROMPT.format(
            query=query,
            hotel_data=truncate(hotel_search_results, 1500),
        )

        response = get_llm().invoke([
            SystemMessage(content=HOTEL_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])

        hotel_data = response.content

    except Exception as e:
        hotel_data = f"Hotel information unavailable: {str(e)}"

    return {
        "hotel_results": hotel_data,
        "messages": [
            AIMessage(content="Hotel recommendations generated.")
        ],
        "llm_calls": bump_llm_calls(state),
    }
