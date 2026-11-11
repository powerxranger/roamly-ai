"""Semantic Router Agent: classifies travel queries and routes execution without keyword matching."""

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.prompts import ROUTER_SYSTEM_PROMPT
from src.clients.llm import get_structured_llm
from src.graph.state import TravelState
from src.models.travel_models import TravelIntent
from src.utils.async_utils import bump_llm_calls


async def router_agent(state: TravelState) -> dict:
    user_query = state.get("user_query", "")
    existing_dest = state.get("destination", "")
    existing_origin = state.get("origin", "")
    has_flights = bool(state.get("flight_results"))
    has_hotels = bool(state.get("hotel_results"))
    has_itinerary = bool(state.get("itinerary"))

    prompt = ROUTER_SYSTEM_PROMPT.format(
        existing_destination=existing_dest or "None (New Session)",
        existing_origin=existing_origin or "None",
        has_flights="Yes" if has_flights else "No",
        has_hotels="Yes" if has_hotels else "No",
        has_itinerary="Yes" if has_itinerary else "No",
        user_query=user_query,
    )

    try:
        # Structured output backed by Pydantic with native json_schema
        structured_llm = get_structured_llm(TravelIntent)
        intent: TravelIntent = await structured_llm.ainvoke([
            SystemMessage(content="You are a precise JSON travel router."),
            HumanMessage(content=prompt),
        ])
    except Exception as e:
        raise RuntimeError(f"RouterAgent failed to classify travel intent: {e}") from e

    intent_dict = intent.model_dump()
    existing_dates = state.get("travel_dates")
    final_travel_dates = intent.travel_dates or existing_dates
    if intent.intent_type == "out_of_scope":
        final_destination = existing_dest
        final_origin = existing_origin
    elif intent.intent_type == "clarification_needed":
        final_destination = intent.destination or existing_dest
        final_origin = intent.origin or existing_origin
    else:
        final_destination = intent.destination or existing_dest or user_query.strip()
        final_origin = intent.origin or existing_origin

    return {
        "intent": intent_dict,
        "destination": final_destination,
        "origin": final_origin,
        "travel_dates": final_travel_dates,
        "llm_calls": bump_llm_calls(state),
    }
