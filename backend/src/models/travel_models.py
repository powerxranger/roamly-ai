"""Typed Pydantic domain models for Roamly AI.
Eliminates regex and string scraping across the entire agentic pipeline.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class TravelIntent(BaseModel):
    """Semantic intent classification produced by the Router Agent."""

    intent_type: Literal[
        "initial_planning",
        "refine_itinerary",
        "update_accommodations",
        "update_transit",
        "general_question",
    ] = Field(
        ...,
        description="Categorization of user request.",
    )
    destination: str = Field(
        ...,
        description="The primary target destination (e.g. 'Tokyo & Kyoto, Japan', 'Bangalore').",
    )
    origin: Optional[str] = Field(
        default=None,
        description="The departure city or origin if specified by the user (e.g. 'Delhi' from 'delhi to bangalore', 'Mumbai', 'New York'). None if unspecified.",
    )
    primary_city: str = Field(
        default="",
        description="The primary single city or municipality for weather forecast querying (e.g. 'Tokyo', 'Rome', 'Paris').",
    )
    duration_days: Optional[int] = Field(
        default=None,
        description="Explicit duration in days if specified or implied by the user (e.g. 3 for 'weekend', 10 for '10 days'). None if unspecified by the user.",
    )
    needs_flights: bool = Field(
        default=False,
        description="True if flight scouting is needed.",
    )
    needs_hotels: bool = Field(
        default=False,
        description="True if accommodation scouting/updating is needed.",
    )
    needs_weather: bool = Field(
        default=False,
        description="True if climate / packing intel is needed.",
    )
    needs_itinerary: bool = Field(
        default=True,
        description="True if day-by-day itinerary needs generation or updating.",
    )
    refinement_summary: str = Field(
        default="",
        description="Semantic description of requested adjustments.",
    )


class FlightInfo(BaseModel):
    """Structured flight intelligence emitted directly by Flight Agent."""

    origin: Optional[str] = Field(default=None, description="Departure location or hub code/name")
    duration: Optional[str] = Field(default=None, description="Typical flight duration, e.g. '2h 45m direct' or '12-14 hrs direct'")
    fare_range: Optional[str] = Field(default=None, description="Estimated airfare range in INR, e.g. '₹7,000 - ₹14,000'")
    airlines: list[str] = Field(default_factory=list, description="Top airlines operating route")
    airports: list[str] = Field(default_factory=list, description="Primary airport codes/names")
    season_tips: Optional[str] = Field(default=None, description="Booking tips and seasonal advice")
    summary: str = Field(default="", description="Executive flight summary")


class HotelOption(BaseModel):
    """Structured accommodation recommendation emitted by Hotel Agent."""

    name: str = Field(..., description="Hotel name")
    tier: Literal["Luxury", "Boutique", "Value", "General"] = Field(
        default="General", description="Accommodation tier"
    )
    price_range: Optional[str] = Field(default=None, description="Estimated nightly rate in INR, e.g. '₹12,000/night'")
    location: Optional[str] = Field(default=None, description="Neighborhood or area")
    amenities: list[str] = Field(default_factory=list, description="Key amenities")
    description: str = Field(default="", description="Hotel summary")


class HotelList(BaseModel):
    """Wrapper for Hotel Agent structured output."""

    hotels: list[HotelOption] = Field(default_factory=list, description="Recommended hotel options")


class ItineraryDayPlan(BaseModel):
    """Structured day schedule emitted directly by Itinerary Agent."""

    day_number: int = Field(..., description="Day index (1, 2, 3...)")
    title: str = Field(..., description="Day theme, e.g. 'Historic Asakusa & Ueno Gardens'")
    morning: Optional[str] = Field(default=None, description="Morning exploration and landmarks")
    afternoon: Optional[str] = Field(default=None, description="Afternoon cultural activity or scenic district")
    evening: Optional[str] = Field(default=None, description="Dinner recommendation or evening event")
    highlights: list[str] = Field(default_factory=list, description="Key bulleted highlights")


class ItineraryPlan(BaseModel):
    """Wrapper for Itinerary Agent structured output."""

    duration_days: Optional[int] = Field(default=None, description="Total days in the itinerary")
    duration_rationale: Optional[str] = Field(default=None, description="Reasoning for recommended trip duration")
    days: list[ItineraryDayPlan] = Field(default_factory=list, description="Ordered daily schedule")


class WeatherPlan(BaseModel):
    """Structured climate and packing recommendations."""

    current_conditions: Optional[str] = Field(default=None, description="Current meteorological conditions")
    temperature: Optional[str] = Field(default=None, description="Expected temperature range, e.g. '18°C - 24°C'")
    forecast_summary: Optional[str] = Field(default=None, description="Weather forecast overview")
    packing_list: list[str] = Field(default_factory=list, description="Recommended essentials to pack")
    source: Optional[str] = Field(default=None, description="Data source: 'openweather' or 'live_search'")



class ExecutiveSynthesis(BaseModel):
    """Structured overview emitted directly by Final Agent."""

    trip_summary: str = Field(..., description="Clear summary of the trip")
    estimated_budget: Optional[str] = Field(default=None, description="Total estimated budget range per traveler")
    recommendations: list[str] = Field(default_factory=list, description="3-4 practical travel tips")


class TripPlan(BaseModel):
    """Unified structured travel plan delivered directly to client (Zero regex required)."""

    destination_title: str = Field(..., description="Destination header")
    origin: Optional[str] = Field(default=None, description="Departure origin if specified")
    duration_label: str = Field(..., description="Duration label, e.g. '7 Days'")
    estimated_budget: Optional[str] = Field(default=None, description="Total budget estimate")
    overview_summary: str = Field(..., description="Trip overview summary")
    flights: FlightInfo = Field(default_factory=FlightInfo)
    hotels: list[HotelOption] = Field(default_factory=list)
    itinerary_days: list[ItineraryDayPlan] = Field(default_factory=list)
    weather: WeatherPlan = Field(default_factory=WeatherPlan)
    recommendations: list[str] = Field(default_factory=list)
