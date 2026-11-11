"""Local Advisor Agent: fast, context-grounded local recommendations and travel Q&A without full pipeline re-execution."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import ADVISOR_SYSTEM_PROMPT
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.mcp_servers.remote import tavily_mcp_search
from src.utils.async_utils import bump_llm_calls, run_async


def _format_itinerary_summary(state: TravelState) -> str:
    """Extract a concise summary of active days to ground local recommendations."""
    itinerary_model = state.get("itinerary_model")
    if itinerary_model and isinstance(itinerary_model, list):
        lines = []
        for day in itinerary_model[:5]:
            day_num = day.get("day_number", "")
            title = day.get("title", "")
            morning = day.get("morning", "")
            lines.append(f"- Day {day_num} ({title}): Morning: {morning}")
        return "\n".join(lines)

    itinerary_text = state.get("itinerary", "")
    if itinerary_text:
        return itinerary_text[:600]

    return "No established itinerary yet."


def advisor_agent(state: TravelState) -> dict:
    user_query = state.get("user_query", "")
    destination = state.get("destination") or "the destination"
    origin = state.get("origin") or "Unspecified"
    itinerary_context = _format_itinerary_summary(state)

    # Targeted real-time web search for authentic local recommendations
    search_context = ""
    try:
        search_query = f"{destination} {user_query} recommendations authentic top spots guide"
        search_results = run_async(tavily_mcp_search(search_query))
        search_context = str(search_results) if search_results else ""
    except Exception as search_err:
        print(f"[AdvisorAgent] Live web search unavailable ({search_err}). Falling back to local knowledge...")
        search_context = f"Local knowledge and recommendations for {destination} regarding: {user_query}."

    prompt = ADVISOR_SYSTEM_PROMPT.format(
        destination=destination,
        origin=origin,
        itinerary_context=itinerary_context,
        user_query=user_query,
        search_context=search_context,
    )

    try:
        llm = get_llm()
        response = llm.invoke([
            SystemMessage(content=f"You are an expert local guide and travel advisor for {destination}."),
            HumanMessage(content=prompt),
        ])
        answer = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        raise RuntimeError(f"AdvisorAgent failed to answer '{user_query}': {e}") from e

    return {
        "messages": [AIMessage(content=answer)],
        "response_type": "conversation",
        "llm_calls": bump_llm_calls(state),
    }
