"""Turns the destination into structured flight guidance using live web search and Pydantic."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import FLIGHT_STRUCTURED_PROMPT
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.mcp_servers.remote import tavily_mcp_search
from src.models.travel_models import FlightInfo
from src.utils.async_utils import bump_llm_calls, run_async, truncate


def flight_agent(state: TravelState):
    intent = state.get("intent") or {}
    existing_model = state.get("flight_model")
    existing_flights = state.get("flight_results", "")

    # Skip scouting if semantic supervisor determined flights are not needed
    if existing_flights and not intent.get("needs_flights", True):
        return {}

    destination = state.get("destination") or state.get("user_query", "")
    origin = state.get("origin") or intent.get("origin") or ""

    try:
        if origin:
            search_query = f"flights from {origin} to {destination} nonstop duration airlines airfare roundtrip INR rupees"
        else:
            search_query = f"flights to {destination} duration airlines airfare roundtrip INR rupees"
        flight_search_results = run_async(tavily_mcp_search(search_query))

        structured_llm = get_llm().with_structured_output(FlightInfo)
        prompt = FLIGHT_STRUCTURED_PROMPT.format(
            origin=origin or "Departure city",
            destination=destination,
            flight_data=truncate(flight_search_results, 1500),
        )

        flight_info: FlightInfo = structured_llm.invoke([
            SystemMessage(content="You are an expert flight data analyst. Emit strictly structured flight data with all fares quoted in Indian Rupees (₹ / INR)."),
            HumanMessage(content=prompt),
        ])
        if origin and not flight_info.origin:
            flight_info.origin = origin

    except Exception as e:
        if existing_model:
            flight_info = FlightInfo(**existing_model)
        else:
            raise RuntimeError(f"FlightAgent failed to scout flight routes for '{destination}': {e}") from e

    model_dict = flight_info.model_dump()
    flight_lines = []
    if flight_info.origin:
        flight_lines.append(f"Departure Origin: {flight_info.origin}")
    if flight_info.duration:
        flight_lines.append(f"Flight Duration: {flight_info.duration}")
    if flight_info.fare_range:
        flight_lines.append(f"Estimated Airfare: {flight_info.fare_range}")
    if flight_info.airlines:
        flight_lines.append(f"Major Airlines: {', '.join(flight_info.airlines)}")
    if flight_info.airports:
        flight_lines.append(f"Serving Airports: {', '.join(flight_info.airports)}")
    if flight_info.season_tips:
        flight_lines.append(f"Booking Advice: {flight_info.season_tips}")
    if flight_info.summary:
        flight_lines.append(f"\n{flight_info.summary}")
    formatted_text = "\n".join(flight_lines)

    return {
        "flight_model": model_dict,
        "flight_results": formatted_text,
        "messages": [
            AIMessage(content="Flight recommendations generated")
        ],
        "llm_calls": bump_llm_calls(state),
    }
