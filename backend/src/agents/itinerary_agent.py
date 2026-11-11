"""Combines flight, hotel, weather, and live web consensus into a structured Pydantic itinerary plan and completed trip synthesis."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import ITINERARY_STRUCTURED_PROMPT
from src.clients.llm import get_structured_llm
from src.graph.state import TravelState
from src.models.travel_models import ItineraryDayPlan, ItineraryPlan
from src.utils.async_utils import bump_llm_calls
from src.utils.plan_builder import assemble_trip_plan


async def itinerary_agent(state: TravelState):
    intent = state.get("intent") or {}
    destination = state.get("destination") or state.get("user_query", "")
    origin = state.get("origin") or intent.get("origin") or ""
    existing_model = state.get("itinerary_model")
    existing_plan = state.get("plan")
    needs_itinerary = intent.get("needs_itinerary", True)

    # If supervisor determined itinerary is not needed:
    if not needs_itinerary:
        # If no established plan or component updates exist, skip execution cleanly
        if not (existing_model or existing_plan or state.get("flight_model") or state.get("hotel_model") or state.get("weather_model")):
            return {}

        # Preserve established itinerary schedule when modifying specific trip components
        days = [ItineraryDayPlan(**d) for d in existing_model] if existing_model else []
        rationale = "Retained established itinerary schedule."
        trip_summary = state.get("trip_summary", "")
        if not trip_summary and existing_plan:
            trip_summary = existing_plan.get("overview_summary", "")
        estimated_budget = state.get("estimated_budget") or (existing_plan.get("estimated_budget") if existing_plan else None)
        recommendations = state.get("recommendations") or (existing_plan.get("recommendations", []) if existing_plan else [])
        refinement_prompts = state.get("refinement_prompts") or (existing_plan.get("refinement_prompts", []) if existing_plan else [])
        llm_increment = 0
    else:
        requested_duration = intent.get("duration_days")

        # If user did not specify duration, scout live internet consensus
        duration_context = ""
        if requested_duration:
            duration_label = f"{requested_duration} Days (User Requested)"
            duration_context = f"The traveler explicitly requested a {requested_duration}-day itinerary."
        elif existing_model:
            duration_label = f"{len(existing_model)} Days (Preserved from prior session)"
            duration_context = f"Maintaining the established {len(existing_model)}-day schedule."
        else:
            duration_label = "Unspecified (Determine based on destination scale and pace)"
            duration_context = "Determine ideal trip duration based on destination scale, major attractions, and relaxed pacing."

        refinement_context = ""
        if existing_model and intent.get("refinement_summary"):
            refinement_context = f"The user requested this specific refinement: '{intent.get('refinement_summary')}'. Incorporate this while preserving unaffected days."
        elif intent.get("refinement_summary"):
            refinement_context = f"Traveler style, companions, and preferences: '{intent.get('refinement_summary')}'. Tailor daily pace, activities, and dining accordingly."

        try:
            structured_llm = get_structured_llm(ItineraryPlan)
            prompt = ITINERARY_STRUCTURED_PROMPT.format(
                destination=destination,
                origin=state.get("origin", "") or "Local or unspecified origin",
                requested_duration=duration_label,
                duration_context=duration_context,
                flight_results=state.get("flight_results", "") or "Direct regional transit.",
                hotel_results=state.get("hotel_results", "") or "Standard accommodations.",
                weather_results=state.get("weather_results", "") or "Seasonal climate.",
                refinement_context=refinement_context or "Initial planning.",
            )

            result: ItineraryPlan = await structured_llm.ainvoke([
                SystemMessage(content="You are an expert travel planner. Determine recommended trip length, architect structured day plans, and synthesize a clear trip overview and budget."),
                HumanMessage(content=prompt),
            ])

            days = result.days
            rationale = result.duration_rationale
            trip_summary = result.trip_summary
            estimated_budget = result.estimated_budget
            recommendations = result.recommendations
            refinement_prompts = result.refinement_prompts
            llm_increment = 1

        except Exception as e:
            if existing_model:
                days = [ItineraryDayPlan(**d) for d in existing_model]
                rationale = "Retained established itinerary schedule."
                trip_summary = state.get("trip_summary", "")
                estimated_budget = state.get("estimated_budget")
                recommendations = state.get("recommendations", [])
                refinement_prompts = state.get("refinement_prompts", [])
                llm_increment = 0
            else:
                raise RuntimeError(f"ItineraryAgent failed to generate itinerary for '{destination}': {e}") from e

    model_dicts = [d.model_dump() for d in days]

    header_text = f"**Duration**: {len(days)} Days"
    if rationale:
        header_text += f" - *{rationale}*\n\n"
    else:
        header_text += "\n\n"

    day_blocks = []
    for d in days:
        d_lines = [f"### Day {d.day_number}: {d.title}"]
        if d.morning:
            d_lines.append(f"- Morning: {d.morning}")
        if d.afternoon:
            d_lines.append(f"- Afternoon: {d.afternoon}")
        if d.evening:
            d_lines.append(f"- Evening: {d.evening}")
        if d.highlights:
            d_lines.extend(f"- Highlight: {h}" for h in d.highlights)
        day_blocks.append("\n".join(d_lines))

    formatted_itinerary = header_text + "\n\n".join(day_blocks)

    # Assemble the clean typed TripPlan model directly (Zero regex)
    structured_plan = assemble_trip_plan(
        destination=destination,
        origin=origin or None,
        overview_summary=trip_summary,
        estimated_budget=estimated_budget,
        recommendations=recommendations,
        flight_data=state.get("flight_model"),
        hotel_data=state.get("hotel_model"),
        itinerary_data=model_dicts,
        weather_data=state.get("weather_model"),
        duration_days=intent.get("duration_days") or (len(days) if days else None),
        refinement_prompts=refinement_prompts,
    )

    budget_line = f"- Total Estimated Budget: {estimated_budget}\n\n" if estimated_budget else ""
    recs_section = (
        f"## Travel Tips\n" + "\n".join(f"- {rec}" for rec in recommendations) + "\n\n"
        if recommendations
        else ""
    )
    refinements_section = (
        f"## Want to Customize?\n" + "\n".join(f"- {p}" for p in refinement_prompts)
        if refinement_prompts
        else ""
    )

    formatted_answer = (
        f"## Trip Summary\n"
        f"{trip_summary}\n\n"
        f"{budget_line}"
        f"{recs_section}"
        f"{refinements_section}"
    ).strip()

    return {
        "itinerary_model": model_dicts,
        "itinerary": formatted_itinerary,
        "trip_summary": trip_summary,
        "estimated_budget": estimated_budget,
        "recommendations": recommendations,
        "refinement_prompts": refinement_prompts,
        "plan": structured_plan,
        "response_type": "plan",
        "messages": [AIMessage(content=formatted_answer)],
        "llm_calls": bump_llm_calls(state, llm_increment),
    }
