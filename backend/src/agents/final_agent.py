"""Formats structured agent outputs into the user-facing executive synthesis and TripPlan (Zero regex)."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import FINAL_STRUCTURED_PROMPT
from src.clients.llm import get_structured_llm
from src.graph.state import TravelState
from src.models.travel_models import ExecutiveSynthesis
from src.utils.async_utils import bump_llm_calls
from src.utils.plan_builder import assemble_trip_plan


def final_agent(state: TravelState):
    destination = state.get("destination") or state.get("user_query", "")
    intent = state.get("intent") or {}
    origin = state.get("origin") or intent.get("origin") or ""

    try:
        structured_llm = get_structured_llm(ExecutiveSynthesis)
        prompt = FINAL_STRUCTURED_PROMPT.format(
            origin=origin or "Departure location",
            destination=destination,
            flight_results=state.get("flight_results", "") or "No transit information available.",
            hotel_results=state.get("hotel_results", "") or "No accommodation information available.",
            weather_results=state.get("weather_results", "") or "No weather information available.",
            itinerary=state.get("itinerary", "") or "No itinerary planned.",
        )

        synthesis: ExecutiveSynthesis = structured_llm.invoke([
            SystemMessage(content="You are a helpful travel planner. Emit a clear trip summary and budget quoting all amounts in Indian Rupees (₹ / INR)."),
            HumanMessage(content=prompt),
        ])

    except Exception as e:
        existing_plan = state.get("plan")
        if existing_plan:
            synthesis = ExecutiveSynthesis(
                trip_summary=existing_plan.get("overview_summary", ""),
                estimated_budget=existing_plan.get("estimated_budget"),
                recommendations=existing_plan.get("recommendations", []),
            )
        else:
            raise RuntimeError(f"FinalAgent failed to synthesize travel plan for '{destination}': {e}") from e

    # Assemble the clean typed TripPlan model (Zero regex)
    structured_plan = assemble_trip_plan(
        destination=destination,
        origin=origin or None,
        overview_summary=synthesis.trip_summary,
        estimated_budget=synthesis.estimated_budget,
        recommendations=synthesis.recommendations,
        flight_data=state.get("flight_model"),
        hotel_data=state.get("hotel_model"),
        itinerary_data=state.get("itinerary_model"),
        weather_data=state.get("weather_model"),
        duration_days=intent.get("duration_days"),
    )

    budget_line = f"- Total Estimated Budget: {synthesis.estimated_budget}\n\n" if synthesis.estimated_budget else ""
    recs_section = (
        f"## Travel Tips\n" + "\n".join(f"- {rec}" for rec in synthesis.recommendations)
        if synthesis.recommendations
        else ""
    )

    formatted_answer = (
        f"## Trip Summary\n"
        f"{synthesis.trip_summary}\n\n"
        f"{budget_line}"
        f"{recs_section}"
    ).strip()

    return {
        "messages": [AIMessage(content=formatted_answer)],
        "plan": structured_plan,
        "llm_calls": bump_llm_calls(state),
    }
