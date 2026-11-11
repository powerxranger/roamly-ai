"""Pure Pydantic assembler for TripPlan. Zero regex matching or string scraping."""

from typing import Any
from src.models.travel_models import (
    FlightInfo,
    HotelOption,
    ItineraryDayPlan,
    TripPlan,
    WeatherPlan,
)


def assemble_trip_plan(
    destination: str,
    overview_summary: str,
    estimated_budget: str | None = None,
    recommendations: list[str] | None = None,
    origin: str | None = None,
    flight_data: dict[str, Any] | None = None,
    hotel_data: list[dict[str, Any]] | None = None,
    itinerary_data: list[dict[str, Any]] | None = None,
    weather_data: dict[str, Any] | None = None,
    duration_days: int | None = None,
    refinement_prompts: list[str] | None = None,
) -> dict[str, Any]:
    """Assemble a typed TripPlan directly from structured agent outputs (No regex)."""

    flights = FlightInfo(**(flight_data or {}))
    if origin and not flights.origin:
        flights.origin = origin
    hotels = [HotelOption(**h) for h in (hotel_data or [])]
    itinerary_days = [ItineraryDayPlan(**d) for d in (itinerary_data or [])]
    weather = WeatherPlan(**(weather_data or {}))

    days_count = len(itinerary_days) or duration_days or 0
    duration_label = f"{days_count} {'Day' if days_count == 1 else 'Days'}" if days_count else ""

    plan = TripPlan(
        destination_title=destination or "",
        origin=origin,
        duration_label=duration_label,
        estimated_budget=estimated_budget,
        overview_summary=overview_summary or (f"Travel plan for {destination}." if destination else ""),
        flights=flights,
        hotels=hotels,
        itinerary_days=itinerary_days,
        weather=weather,
        recommendations=recommendations or [],
        refinement_prompts=refinement_prompts or [],
    )

    return plan.model_dump()
