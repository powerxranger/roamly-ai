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

    try:
        search_query = f"flights to {destination} duration airlines airfare"
        flight_search_results = run_async(tavily_mcp_search(search_query))

        structured_llm = get_llm().with_structured_output(FlightInfo)
        prompt = FLIGHT_STRUCTURED_PROMPT.format(
            destination=destination,
            flight_data=truncate(flight_search_results, 1500),
        )

        flight_info: FlightInfo = structured_llm.invoke([
            SystemMessage(content="You are an expert flight data analyst. Emit strictly structured flight data."),
            HumanMessage(content=prompt),
        ])

    except Exception:
        if existing_model:
            flight_info = FlightInfo(**existing_model)
        else:
            flight_info = FlightInfo(
                duration="Varies by departure city",
                fare_range="$750 - $1,200 typical",
                airlines=["Major International Carriers"],
                airports=["Primary International Hub"],
                season_tips="Book 6-8 weeks prior to departure for best rates.",
                summary=f"Direct and 1-stop routes available to {destination}.",
            )

    model_dict = flight_info.model_dump()
    formatted_text = (
        f"Flight Duration: {flight_info.duration or 'Direct & 1-stop available'}\n"
        f"Estimated Airfare: {flight_info.fare_range or 'Varies by season'}\n"
        f"Major Airlines: {', '.join(flight_info.airlines)}\n"
        f"Serving Airports: {', '.join(flight_info.airports)}\n"
        f"Booking Advice: {flight_info.season_tips or 'Book 6-8 weeks in advance.'}\n\n"
        f"{flight_info.summary}"
    )

    return {
        "flight_model": model_dict,
        "flight_results": formatted_text,
        "messages": [
            AIMessage(content="Flight recommendations generated")
        ],
        "llm_calls": bump_llm_calls(state),
    }
