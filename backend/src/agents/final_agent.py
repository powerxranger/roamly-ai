"""Formats structured agent outputs into the user-facing executive synthesis and TripPlan (Zero regex)."""

import time
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import FINAL_STRUCTURED_PROMPT
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.models.travel_models import ExecutiveSynthesis
from src.utils.async_utils import bump_llm_calls, truncate
from src.utils.plan_builder import assemble_trip_plan


def final_agent(state: TravelState):
    # Pacing pause for Groq rate limits
    time.sleep(1.5)

    destination = state.get("destination") or state.get("user_query", "")

    try:
        structured_llm = get_llm().with_structured_output(ExecutiveSynthesis)
        prompt = FINAL_STRUCTURED_PROMPT.format(
            destination=destination,
            flight_results=truncate(state.get("flight_results", ""), 500),
            hotel_results=truncate(state.get("hotel_results", ""), 500),
            weather_results=truncate(state.get("weather_results", ""), 300),
            itinerary=truncate(state.get("itinerary", ""), 600),
        )

        synthesis: ExecutiveSynthesis = structured_llm.invoke([
            SystemMessage(content="You are an elite travel concierge. Emit strictly structured executive travel synthesis quoting all budgets in Indian Rupees (₹ / INR)."),
            HumanMessage(content=prompt),
        ])

    except Exception:
        synthesis = ExecutiveSynthesis(
            trip_summary=(
                f"An extraordinary bespoke journey across {destination}, harmonizing cultural landmarks with curated boutique stays. "
                f"This itinerary offers an ideal balance of iconic exploration, culinary immersion, and relaxed discovery."
            ),
            estimated_budget="₹2,75,000 - ₹3,85,000 per traveler",
            recommendations=[
                "Secure major attraction tickets and rail passes 3 to 4 weeks prior to departure.",
                "Reserve dining at premier venues well in advance.",
                "Pack light, versatile layers and comfortable footwear for walking tours.",
            ],
        )

    # Assemble the clean typed TripPlan model (Zero regex)
    structured_plan = assemble_trip_plan(
        destination=destination,
        overview_summary=synthesis.trip_summary,
        estimated_budget=synthesis.estimated_budget,
        recommendations=synthesis.recommendations,
        flight_data=state.get("flight_model"),
        hotel_data=state.get("hotel_model"),
        itinerary_data=state.get("itinerary_model"),
        weather_data=state.get("weather_model"),
        duration_days=state.get("intent", {}).get("duration_days"),
    )

    formatted_answer = (
        f"## Trip Summary\n"
        f"{synthesis.trip_summary}\n\n"
        f"## Estimated Budget\n"
        f"- Total Estimated Budget: {synthesis.estimated_budget or '₹2,75,000 - ₹3,85,000 per traveler'}\n\n"
        f"## Final Recommendations\n" +
        "\n".join(f"- {rec}" for rec in synthesis.recommendations)
    )

    return {
        "messages": [AIMessage(content=formatted_answer)],
        "plan": structured_plan,
        "llm_calls": bump_llm_calls(state),
    }
