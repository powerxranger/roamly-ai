"""Unit tests verifying zero-regex, schema-driven Pydantic architecture."""

import pytest
from src.models.travel_models import (
    FlightInfo,
    HotelOption,
    ItineraryDayPlan,
    TravelIntent,
    TripPlan,
    WeatherPlan,
)
from src.utils.plan_builder import assemble_trip_plan


def test_travel_intent_validation():
    data = {
        "intent_type": "initial_planning",
        "destination": "Kyoto & Tokyo, Japan",
        "primary_city": "Kyoto",
        "duration_days": 7,
        "needs_flights": True,
        "needs_hotels": True,
        "needs_weather": True,
        "needs_itinerary": True,
        "refinement_summary": "",
    }
    intent = TravelIntent(**data)
    assert intent.intent_type == "initial_planning"
    assert intent.destination == "Kyoto & Tokyo, Japan"
    assert intent.primary_city == "Kyoto"
    assert intent.duration_days == 7
    assert intent.needs_flights is True
    assert intent.needs_hotels is True
    assert intent.needs_weather is True
    assert intent.needs_itinerary is True


def test_travel_intent_unspecified_duration():
    data = {
        "intent_type": "initial_planning",
        "destination": "Amsterdam",
        "primary_city": "Amsterdam",
        "needs_itinerary": True,
    }
    intent = TravelIntent(**data)
    assert intent.duration_days is None
    assert intent.destination == "Amsterdam"


def test_assemble_trip_plan_zero_regex():
    flight_data = {
        "duration": "12 hours",
        "fare_range": "₹75,000 - ₹95,000",
        "airlines": ["ANA", "JAL"],
        "airports": ["HND", "NRT"],
        "season_tips": "Book 6 weeks ahead",
        "summary": "Great direct flight options available.",
    }
    hotel_data = [
        {
            "name": "The Ritz-Carlton Kyoto",
            "tier": "Luxury",
            "price_range": "₹65,000/night",
            "location": "Kamigyo Ward",
            "amenities": ["Spa", "Michelin Dining"],
            "description": "Riverside hotel.",
        }
    ]
    itinerary_data = [
        {
            "day_number": 1,
            "title": "Arrival in Kyoto",
            "morning": "Flight arrival and check-in",
            "afternoon": "Stroll Gion district",
            "evening": "Welcome Kaiseki dinner",
            "highlights": ["Gion", "Kaiseki"],
        }
    ]
    weather_data = {
        "current_conditions": "Clear, 60% humidity",
        "temperature": "22°C",
        "forecast_summary": "Mild autumn weather expected.",
        "packing_list": ["Comfortable shoes", "Light jacket"],
    }

    plan_dict = assemble_trip_plan(
        destination="Kyoto, Japan",
        overview_summary="Complete travel plan for Kyoto.",
        estimated_budget="₹3,20,000 - ₹4,50,000",
        recommendations=["Book temple passes early"],
        flight_data=flight_data,
        hotel_data=hotel_data,
        itinerary_data=itinerary_data,
        weather_data=weather_data,
        duration_days=5,
    )

    assert plan_dict["destination_title"] == "Kyoto, Japan"
    assert len(plan_dict["hotels"]) == 1
    assert plan_dict["hotels"][0]["name"] == "The Ritz-Carlton Kyoto"
    assert plan_dict["hotels"][0]["price_range"] == "₹65,000/night"
    assert len(plan_dict["itinerary_days"]) == 1
    assert plan_dict["itinerary_days"][0]["day_number"] == 1
    assert plan_dict["weather"]["temperature"] == "22°C"
    assert plan_dict["flights"]["airlines"] == ["ANA", "JAL"]
    assert plan_dict["flights"]["fare_range"] == "₹75,000 - ₹95,000"
