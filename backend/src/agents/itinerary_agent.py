"""Combines flight, hotel, weather, and live web consensus into a structured Pydantic itinerary plan."""

import time
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import ITINERARY_STRUCTURED_PROMPT
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.mcp_servers.remote import tavily_mcp_search
from src.models.travel_models import ItineraryDayPlan, ItineraryPlan
from src.utils.async_utils import bump_llm_calls, run_async, truncate


def itinerary_agent(state: TravelState):
    intent = state.get("intent") or {}
    existing_model = state.get("itinerary_model")
    existing_itinerary = state.get("itinerary", "")
    needs_itinerary = intent.get("needs_itinerary", True)

    # If itinerary exists and user only changed stays or transit
    if existing_itinerary and not needs_itinerary:
        return {}

    # Pacing pause for Groq rate limits
    time.sleep(1.5)

    destination = state.get("destination") or state.get("user_query", "")
    requested_duration = intent.get("duration_days")

    # If user didn't specify duration, scout live internet consensus
    duration_context = ""
    if requested_duration:
        duration_label = f"{requested_duration} Days (User Requested)"
        duration_context = f"The traveler explicitly requested a {requested_duration}-day itinerary."
    elif existing_model:
        duration_label = f"{len(existing_model)} Days (Preserved from prior session)"
        duration_context = f"Maintaining the established {len(existing_model)}-day schedule."
    else:
        duration_label = "Unspecified (Determine based on travel guide consensus)"
        try:
            search_query = f"how many days to visit {destination} recommended itinerary duration travel guide"
            search_res = run_async(tavily_mcp_search(search_query))
            duration_context = truncate(search_res, 1000)
        except Exception:
            duration_context = ""

    refinement_context = ""
    if existing_model and intent.get("refinement_summary"):
        refinement_context = f"The user requested this specific refinement: '{intent.get('refinement_summary')}'. Incorporate this while preserving unaffected days."

    try:
        structured_llm = get_llm().with_structured_output(ItineraryPlan)
        prompt = ITINERARY_STRUCTURED_PROMPT.format(
            destination=destination,
            requested_duration=duration_label,
            duration_context=duration_context,
            flight_results=truncate(state.get("flight_results", ""), 600),
            hotel_results=truncate(state.get("hotel_results", ""), 600),
            weather_results=truncate(state.get("weather_results", ""), 400),
            refinement_context=refinement_context or "Initial planning.",
        )

        result: ItineraryPlan = structured_llm.invoke([
            SystemMessage(content="You are an elite travel architect. Determine optimal trip length from travel consensus and emit structured day plans."),
            HumanMessage(content=prompt),
        ])

        days = result.days
        rationale = result.duration_rationale

    except Exception as e:
        if existing_model:
            days = [ItineraryDayPlan(**d) for d in existing_model]
            rationale = "Retained established itinerary schedule."
        else:
            raise RuntimeError(f"ItineraryAgent failed to generate itinerary for '{destination}': {e}") from e

    model_dicts = [d.model_dump() for d in days]

    header_text = f"**Duration**: {len(days)} Days"
    if rationale:
        header_text += f" - *{rationale}*\n\n"
    else:
        header_text += "\n\n"

    formatted_text = header_text + "\n\n".join([
        f"### Day {d.day_number}: {d.title}\n"
        f"- Morning: {d.morning or 'Morning exploration'}\n"
        f"- Afternoon: {d.afternoon or 'Afternoon cultural discovery'}\n"
        f"- Evening: {d.evening or 'Evening dining and relaxation'}\n" +
        "\n".join(f"- Highlight: {h}" for h in d.highlights)
        for d in days
    ])

    return {
        "itinerary_model": model_dicts,
        "itinerary": formatted_text,
        "messages": [
            AIMessage(content="Itinerary generated")
        ],
        "llm_calls": bump_llm_calls(state),
    }
