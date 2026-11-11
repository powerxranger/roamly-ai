"""Local Advisor Agent: fast, context-grounded local recommendations and travel Q&A without full pipeline re-execution."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import ADVISOR_SYSTEM_PROMPT
from src.clients.llm import get_structured_llm
from src.graph.state import TravelState
from src.mcp_servers.remote import tavily_mcp_search
from src.models.travel_models import AdvisorResponse
from src.utils.async_utils import bump_llm_calls


def _format_itinerary_summary(state: TravelState) -> str:
    """Extract a full summary of active days to ground local recommendations."""
    itinerary_model = state.get("itinerary_model")
    if itinerary_model and isinstance(itinerary_model, list):
        lines = []
        for day in itinerary_model:
            day_num = day.get("day_number", "")
            title = day.get("title", "")
            morning = day.get("morning", "")
            afternoon = day.get("afternoon", "")
            evening = day.get("evening", "")
            details = [d for d in [morning, afternoon, evening] if d]
            summary_part = f" - {', '.join(details)}" if details else ""
            lines.append(f"- Day {day_num} ({title}){summary_part}")
        return "\n".join(lines)

    itinerary_text = state.get("itinerary", "")
    if itinerary_text and itinerary_text.strip():
        return itinerary_text.strip()

    return "No established itinerary yet."


async def advisor_agent(state: TravelState) -> dict:
    user_query = state.get("user_query", "")
    destination = state.get("destination") or "the destination"
    origin = state.get("origin") or "Unspecified"
    itinerary_context = _format_itinerary_summary(state)

    # Targeted real-time web search for authentic local recommendations
    search_context = ""
    try:
        search_query = f"{destination} {user_query} recommendations authentic top spots"
        search_results = await tavily_mcp_search(search_query)
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
        structured_llm = get_structured_llm(AdvisorResponse)
        response = await structured_llm.ainvoke([
            SystemMessage(content=f"You are an expert local guide and travel advisor for {destination}."),
            HumanMessage(content=prompt),
        ])
        if isinstance(response, AdvisorResponse):
            answer = response.answer
            followup_suggestions = response.followup_suggestions or []
        elif isinstance(response, dict):
            answer = response.get("answer", "")
            followup_suggestions = response.get("followup_suggestions", [])
        else:
            answer = getattr(response, "answer", str(response))
            followup_suggestions = getattr(response, "followup_suggestions", [])
    except Exception as e:
        raise RuntimeError(f"AdvisorAgent failed to answer '{user_query}': {e}") from e

    return {
        "messages": [AIMessage(content=answer)],
        "response_type": "conversation",
        "followup_suggestions": followup_suggestions,
        "llm_calls": bump_llm_calls(state),
    }
