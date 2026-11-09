"""Finds hotel options for the destination through Tavily and emits structured Pydantic models."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.prompts import HOTEL_STRUCTURED_PROMPT
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.mcp_servers.remote import tavily_mcp_search
from src.models.travel_models import HotelList, HotelOption
from src.utils.async_utils import bump_llm_calls, run_async, truncate


def hotel_agent(state: TravelState):
    intent = state.get("intent") or {}
    existing_model = state.get("hotel_model")
    existing_hotels = state.get("hotel_results", "")

    # Skip scouting if semantic supervisor determined accommodations are not needed
    if existing_hotels and not intent.get("needs_hotels", True):
        return {}

    destination = state.get("destination") or state.get("user_query", "")

    try:
        search_query = f"best hotels accommodations in {destination} luxury boutique rates INR rupees per night"
        hotel_search_results = run_async(tavily_mcp_search(search_query))

        structured_llm = get_llm().with_structured_output(HotelList)
        prompt = HOTEL_STRUCTURED_PROMPT.format(
            destination=destination,
            hotel_data=truncate(hotel_search_results, 1500),
        )

        result: HotelList = structured_llm.invoke([
            SystemMessage(content="You are an expert travel assistant. Emit structured hotel options with all nightly rates quoted in Indian Rupees (₹ / INR)."),
            HumanMessage(content=prompt),
        ])

        hotels = result.hotels

    except Exception as e:
        if existing_model:
            hotels = [HotelOption(**h) for h in existing_model]
        else:
            raise RuntimeError(f"HotelAgent failed to scout accommodations for '{destination}': {e}") from e

    model_dicts = [h.model_dump() for h in hotels]

    formatted_text = "\n\n".join([
        f"### {h.tier}: **{h.name}**\n"
        f"- Nightly Rate: {h.price_range or 'Rates on request'}\n"
        f"- Location: {h.location or destination}\n"
        f"- Amenities: {', '.join(h.amenities)}\n"
        f"- Overview: {h.description}"
        for h in hotels
    ])

    return {
        "hotel_model": model_dicts,
        "hotel_results": formatted_text,
        "messages": [
            AIMessage(content="Hotel recommendations generated.")
        ],
        "llm_calls": bump_llm_calls(state),
    }
