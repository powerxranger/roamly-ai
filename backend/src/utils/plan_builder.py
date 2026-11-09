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
    estimated_budget: str | None,
    recommendations: list[str],
    flight_data: dict[str, Any] | None = None,
    hotel_data: list[dict[str, Any]] | None = None,
    itinerary_data: list[dict[str, Any]] | None = None,
    weather_data: dict[str, Any] | None = None,
    duration_days: int | None = None,
) -> dict[str, Any]:
    """Assemble a typed TripPlan directly from structured agent outputs (No regex)."""

    flights = FlightInfo(**(flight_data or {}))
    hotels = [HotelOption(**h) for h in (hotel_data or [])]
    itinerary_days = [ItineraryDayPlan(**d) for d in (itinerary_data or [])]
    weather = WeatherPlan(**(weather_data or {}))

    days_count = len(itinerary_days) or duration_days or 5
    duration_label = f"{days_count} Days"

    plan = TripPlan(
        destination_title=destination or "Bespoke Journey",
        duration_label=duration_label,
        estimated_budget=estimated_budget or "$3,200 - $4,800 per traveler",
        overview_summary=overview_summary or "Bespoke travel plan curated by autonomous concierges.",
        flights=flights,
        hotels=hotels,
        itinerary_days=itinerary_days,
        weather=weather,
        recommendations=recommendations or [
            "Secure high-speed rail passes prior to arrival for seamless transit.",
            "Make reservations for signature dining at least 4 weeks in advance.",
            "Carry a compact universal power bank during full-day excursions.",
        ],
    )

    return plan.model_dump()
