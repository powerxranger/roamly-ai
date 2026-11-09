"""Combines flight, hotel, and weather intelligence into a structured Pydantic itinerary plan."""

import time
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import ITINERARY_STRUCTURED_PROMPT
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.models.travel_models import ItineraryDayPlan, ItineraryPlan
from src.utils.async_utils import bump_llm_calls, truncate


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
    duration_days = intent.get("duration_days") or (len(existing_model) if existing_model else 7) or 7

    refinement_context = ""
    if existing_model and intent.get("refinement_summary"):
        refinement_context = f"The user requested this specific refinement: '{intent.get('refinement_summary')}'. Incorporate this while preserving unaffected days."

    try:
        structured_llm = get_llm().with_structured_output(ItineraryPlan)
        prompt = ITINERARY_STRUCTURED_PROMPT.format(
            destination=destination,
            duration_days=duration_days,
            flight_results=truncate(state.get("flight_results", ""), 600),
            hotel_results=truncate(state.get("hotel_results", ""), 600),
            weather_results=truncate(state.get("weather_results", ""), 400),
            refinement_context=refinement_context or "Initial planning.",
        )

        result: ItineraryPlan = structured_llm.invoke([
            SystemMessage(content="You are an elite travel architect. Emit strictly structured day plans."),
            HumanMessage(content=prompt),
        ])

        days = result.days

    except Exception:
        if existing_model:
            days = [ItineraryDayPlan(**d) for d in existing_model]
        else:
            days = [
                ItineraryDayPlan(
                    day_number=1,
                    title=f"Arrival & Orientation in {destination}",
                    morning="Arrival, airport transfer, and hotel check-in.",
                    afternoon=f"Introductory stroll through the historic center of {destination}.",
                    evening="Welcome dinner at a traditional local bistro.",
                    highlights=["Airport transit", "Neighborhood orientation", "Dinner"],
                ),
                ItineraryDayPlan(
                    day_number=2,
                    title="Iconic Landmarks & Cultural Highlights",
                    morning="Morning visit to primary historic landmarks and viewpoints.",
                    afternoon="Guided exploration of renowned cultural museums or gardens.",
                    evening="Scenic twilight walk and artisanal culinary experience.",
                    highlights=["Landmark exploration", "Cultural immersion", "Evening tasting"],
                ),
                ItineraryDayPlan(
                    day_number=3,
                    title="Neighborhood Gems & Scenic Excursion",
                    morning="Local market tour and artisanal coffee tasting.",
                    afternoon="Scenic transit or day excursion to nearby picturesque vistas.",
                    evening="Relaxed dinner featuring regional delicacies.",
                    highlights=["Market tour", "Scenic excursion", "Regional dining"],
                ),
            ]

    model_dicts = [d.model_dump() for d in days]

    formatted_text = "\n\n".join([
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
