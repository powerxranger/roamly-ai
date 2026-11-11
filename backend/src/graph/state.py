"""Shared state passed between every node of the travel graph."""

import operator
from typing import Annotated, Any, Optional, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage


class TravelState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    weather_results: str
    itinerary: str
    llm_calls: Annotated[int, operator.add]

    # Structured Pydantic state (Zero regex / string scraping)
    destination: str
    origin: str
    travel_dates: Optional[str]
    intent: Optional[dict[str, Any]]
    flight_model: Optional[dict[str, Any]]
    hotel_model: Optional[list[dict[str, Any]]]
    itinerary_model: Optional[list[dict[str, Any]]]
    weather_model: Optional[dict[str, Any]]
    trip_summary: Optional[str]
    estimated_budget: Optional[str]
    recommendations: Optional[list[str]]
    followup_suggestions: Optional[list[str]]
    plan: Optional[dict[str, Any]]
    followup_history: list[str]
    response_type: Optional[str]


def initial_state(user_query: str) -> TravelState:
    """Build the empty state the graph starts from."""
    return {
        "messages": [HumanMessage(content=user_query)],
        "user_query": user_query,
        "flight_results": "",
        "hotel_results": "",
        "weather_results": "",
        "itinerary": "",
        "llm_calls": 0,
        "destination": "",
        "origin": "",
        "travel_dates": None,
        "intent": None,
        "flight_model": None,
        "hotel_model": None,
        "itinerary_model": None,
        "weather_model": None,
        "trip_summary": "",
        "estimated_budget": "",
        "recommendations": [],
        "followup_suggestions": [],
        "plan": None,
        "followup_history": [],
        "response_type": "plan",
    }
