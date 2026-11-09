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


class TransitOption(BaseModel):
    """Details for an alternative travel medium like train, car, or road bus."""

    mode: str = Field(..., description="Transport mode: e.g. 'Train', 'Road / Drive', 'Flight', 'Bus'")
    duration: Optional[str] = Field(default=None, description="Travel duration, e.g. '3h 45m'")
    fare_range: Optional[str] = Field(default=None, description="Estimated fare in INR, e.g. '₹900 - ₹1,800'")
    operators: list[str] = Field(default_factory=list, description="Key train names, bus operators, or highway names (e.g. ['Vande Bharat Express', 'Shatabdi'])")
    terminals: list[str] = Field(default_factory=list, description="Departure and arrival stations or hubs (e.g. ['New Delhi (NDLS)', 'Jaipur (JP)'])")
    details: Optional[str] = Field(default=None, description="Practical travel guidance, distance, or route tips")


class FlightInfo(BaseModel):
    """Structured transit intelligence (flights, trains, and road/driving) emitted directly by Flight/Transit Agent."""

    origin: Optional[str] = Field(default=None, description="Departure location or hub city/town")
    destination: Optional[str] = Field(default=None, description="Arrival destination city/town")
    route_type: Optional[str] = Field(
        default=None,
        description="Type of route, e.g. 'Short Regional Route', 'Domestic Direct', 'Connecting Flight', or 'Multi-modal'",
    )
    primary_mode: Optional[str] = Field(
        default=None,
        description="Recommended primary mode of transit: 'Train', 'Road / Drive', 'Flight', or 'Multi-modal'",
    )
    mode_recommendation: Optional[str] = Field(
        default=None,
        description="Clear rationale explaining why the recommended mode is best for this specific route distance and convenience",
    )
    departure_airport: Optional[str] = Field(
        default=None,
        description="Serving commercial departure airport (e.g. 'Indira Gandhi International (DEL)' or nearest airport if origin has no commercial airport, like 'Dehradun Jolly Grant Airport (DED)')",
    )
    arrival_airport: Optional[str] = Field(
        default=None,
        description="Serving commercial arrival airport (e.g. 'Kempegowda International (BLR)' or nearest airport if destination has no commercial airport, like 'Hubli Airport (HBX)')",
    )
    origin_to_airport_transit: Optional[str] = Field(
        default=None,
        description="Ground transit from origin city to departure airport if origin city has no airport (e.g. 'Cab or bus from Rishikesh to Dehradun Airport (~35 km, 45-60 mins)')",
    )
    airport_to_destination_transit: Optional[str] = Field(
        default=None,
        description="Ground transit from arrival airport to destination city if destination city has no airport (e.g. 'Cab or train from Hubli/Jindal Airport to Hampi (~40-140 km, 1-3 hrs)')",
    )
    duration: Optional[str] = Field(default=None, description="Typical flight duration, e.g. '2h 45m direct', or null if flying is not recommended")
    fare_range: Optional[str] = Field(default=None, description="Estimated airfare range in INR, e.g. '₹7,000 - ₹14,000'")
    airlines: list[str] = Field(default_factory=list, description="Top airlines operating route")
    airports: list[str] = Field(default_factory=list, description="Primary airport codes/names")
    train_option: Optional[TransitOption] = Field(
        default=None,
        description="Train / Rail alternative if viable (duration, train names like Vande Bharat/Rajdhani, fare, stations)",
    )
    road_option: Optional[TransitOption] = Field(
        default=None,
        description="Road / Drive / Bus alternative if viable (duration, highway route, cab/bus fare estimate, distance)",
    )
    season_tips: Optional[str] = Field(default=None, description="Booking tips and seasonal advice")
    summary: str = Field(default="", description="Executive route and transit summary")


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
