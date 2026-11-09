"""Turns the destination into structured flight guidance using live web search and Pydantic."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import FLIGHT_STRUCTURED_PROMPT
from src.clients.llm import get_structured_llm
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
            search_query = f"how to travel from {origin} to {destination} flights train road bus distance duration fare INR"
        else:
            search_query = f"how to reach {destination} nearest airport flights train bus road distance duration INR rupees"
        flight_search_results = run_async(tavily_mcp_search(search_query))

        structured_llm = get_structured_llm(FlightInfo)
        prompt = FLIGHT_STRUCTURED_PROMPT.format(
            origin=origin or "Departure city",
            destination=destination,
            flight_data=truncate(flight_search_results, 1500),
        )

        flight_info: FlightInfo = structured_llm.invoke([
            SystemMessage(content="You are an expert travel and transit analyst. Emit strictly structured transit data covering flights, trains, and road options with all fares quoted in Indian Rupees (₹ / INR)."),
            HumanMessage(content=prompt),
        ])
        if origin and not flight_info.origin:
            flight_info.origin = origin
        if destination and not flight_info.destination:
            flight_info.destination = destination

    except Exception as e:
        if existing_model:
            flight_info = FlightInfo(**existing_model)
        else:
            raise RuntimeError(f"FlightAgent failed to scout flight routes for '{destination}': {e}") from e

    model_dict = flight_info.model_dump()
    flight_lines = []
    if flight_info.origin:
        flight_lines.append(f"Departure Origin: {flight_info.origin}")
    if flight_info.destination:
        flight_lines.append(f"Arrival Destination: {flight_info.destination}")
    if flight_info.primary_mode:
        flight_lines.append(f"Recommended Transit Mode: {flight_info.primary_mode}")
    if flight_info.mode_recommendation:
        flight_lines.append(f"Mode Advice: {flight_info.mode_recommendation}")
    if flight_info.route_type:
        flight_lines.append(f"Route Type: {flight_info.route_type}")
    if flight_info.duration:
        flight_lines.append(f"Flight Option: {flight_info.duration} (Airfare: {flight_info.fare_range or 'Varies'})")
        if flight_info.airlines:
            flight_lines.append(f"Airlines: {', '.join(flight_info.airlines)}")
    if flight_info.departure_airport:
        flight_lines.append(f"Departure Airport: {flight_info.departure_airport}")
    if flight_info.origin_to_airport_transit:
        flight_lines.append(f"Origin Ground Transfer: {flight_info.origin_to_airport_transit}")
    if flight_info.arrival_airport:
        flight_lines.append(f"Arrival Airport: {flight_info.arrival_airport}")
    if flight_info.airport_to_destination_transit:
        flight_lines.append(f"Arrival Ground Transfer: {flight_info.airport_to_destination_transit}")
    if flight_info.train_option:
        train = flight_info.train_option
        flight_lines.append(f"Train Option: {train.duration or ''} (Fare: {train.fare_range or ''}) via {', '.join(train.operators) if train.operators else 'Express Train'} - {train.details or ''}")
    if flight_info.road_option:
        road = flight_info.road_option
        flight_lines.append(f"Road Option: {road.duration or ''} (Cost: {road.fare_range or ''}) via {', '.join(road.operators) if road.operators else 'Highway'} - {road.details or ''}")
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
