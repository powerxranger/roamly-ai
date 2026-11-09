"""Semantic Router Agent: classifies travel queries and routes execution without keyword matching."""

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from src.agents.prompts import ROUTER_SYSTEM_PROMPT
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.models.travel_models import TravelIntent
from src.utils.async_utils import bump_llm_calls


def router_agent(state: TravelState) -> dict:
    user_query = state.get("user_query", "")
    existing_dest = state.get("destination", "")
    has_flights = bool(state.get("flight_results"))
    has_hotels = bool(state.get("hotel_results"))
    has_itinerary = bool(state.get("itinerary"))

    prompt = ROUTER_SYSTEM_PROMPT.format(
        existing_destination=existing_dest or "None (New Session)",
        has_flights="Yes" if has_flights else "No",
        has_hotels="Yes" if has_hotels else "No",
        has_itinerary="Yes" if has_itinerary else "No",
        user_query=user_query,
    )

    llm = get_llm()

    try:
        # Structured output backed by Pydantic
        structured_llm = llm.with_structured_output(TravelIntent)
        intent: TravelIntent = structured_llm.invoke([
            SystemMessage(content="You are a precise JSON travel router."),
            HumanMessage(content=prompt),
        ])
    except (ValidationError, Exception):
        is_initial = not (has_flights or has_hotels or has_itinerary)
        intent = TravelIntent(
            intent_type="initial_planning" if is_initial else "refine_itinerary",
            destination=existing_dest or "Custom Journey",
            duration_days=None,
            needs_flights=is_initial,
            needs_hotels=is_initial,
            needs_weather=is_initial,
            needs_itinerary=True,
            refinement_summary=user_query if not is_initial else "",
        )

    intent_dict = intent.model_dump()
    final_destination = intent.destination or existing_dest or "Custom Journey"

    return {
        "intent": intent_dict,
        "destination": final_destination,
        "llm_calls": bump_llm_calls(state),
    }
