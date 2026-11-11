"""Typed Pydantic domain models for Roamly AI.
Eliminates regex and string scraping across the entire agentic pipeline.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class TravelIntent(BaseModel):
    """Semantic intent classification produced by the Router Agent."""

    intent_type: Literal[
        "initial_planning",
        "refine_itinerary",
        "update_accommodations",
        "update_transit",
        "general_question",
        "out_of_scope",
        "clarification_needed",
    ] = Field(
        default="initial_planning",
        description="Categorization of user request.",
    )
    destination: Optional[str] = Field(
        default="",
        description="The primary target destination (e.g. 'Tokyo & Kyoto, Japan', 'Bangalore'). Leave empty if out of scope or unspecified.",
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
    travel_dates: Optional[str] = Field(
        default=None,
        description="Explicit travel dates, timeline, month, or season if specified by the user (e.g. 'next weekend', 'Dec 20 to Dec 25', 'December', 'in summer'). None if unspecified.",
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
    flight_search_query: Optional[str] = Field(
        default=None,
        description="Targeted 3 to 8 word search query for flights, trains, road routes, or local transit passes if needs_flights is true. None otherwise.",
    )
    hotel_search_query: Optional[str] = Field(
        default=None,
        description="Targeted 3 to 8 word search query for accommodations matching traveler budget and style if needs_hotels is true. None otherwise.",
    )
    guardrail_message: Optional[str] = Field(
        default=None,
        description="Direct boundary response or clarifying travel guidance when intent is out_of_scope or clarification_needed.",
    )

    @field_validator("destination", mode="before")
    @classmethod
    def coerce_destination(cls, v):
        return "" if v is None else str(v).strip()


class TransitOption(BaseModel):
    """Details for an alternative travel medium like train, car, or road bus."""

    mode: str = Field(..., description="Transport mode: e.g. 'Train', 'Road / Drive', 'Flight', 'Bus'")
    duration: Optional[str] = Field(default=None, description="Travel duration, e.g. '3h 45m'")
    fare_range: Optional[str] = Field(default=None, description="Estimated fare in local or requested currency, e.g. '$35 - $60' or '₹900 - ₹1,800'")
    operators: Optional[list[str]] = Field(default_factory=list, description="Key train names, bus operators, or highway names (e.g. ['Eurostar', 'Shinkansen', 'Vande Bharat Express', 'Amtrak'])")
    terminals: Optional[list[str]] = Field(default_factory=list, description="Departure and arrival stations or hubs (e.g. ['Paris Gare du Nord', 'London St Pancras'] or ['New Delhi (NDLS)', 'Jaipur (JP)'])")
    details: Optional[str] = Field(default=None, description="Practical travel guidance, distance, or route tips")

    @field_validator("operators", "terminals", mode="before")
    @classmethod
    def coerce_transit_lists(cls, v):
        return [] if v is None else v


class TransitInfo(BaseModel):
    """Structured multi-modal transit intelligence (flights, trains, and road/driving)."""

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
        description="Serving commercial departure airport (e.g. 'JFK', 'LHR', 'DEL', or nearest regional airport if origin has no commercial airport)",
    )
    arrival_airport: Optional[str] = Field(
        default=None,
        description="Serving commercial arrival airport (e.g. 'HND', 'CDG', 'BLR', or nearest regional airport if destination has no commercial airport)",
    )
    origin_to_airport_transit: Optional[str] = Field(
        default=None,
        description="Ground transit from origin city to departure airport if origin city has no airport (e.g. 'Cab or shuttle to nearest regional airport (~35 km, 45 mins)')",
    )
    airport_to_destination_transit: Optional[str] = Field(
        default=None,
        description="Ground transit from arrival airport to destination city if destination city has no airport (e.g. 'Cab or train from arrival airport to destination (~50 km, 1 hour)')",
    )
    duration: Optional[str] = Field(default=None, description="Typical flight duration, e.g. '2h 45m direct', or null if flying is not recommended")
    fare_range: Optional[str] = Field(default=None, description="Estimated airfare range in local or requested currency, e.g. '$450 - $700' or '₹12,000 - ₹18,000'")
    airlines: Optional[list[str]] = Field(default_factory=list, description="Top airlines operating route, or empty list if flying is not viable")
    airports: Optional[list[str]] = Field(default_factory=list, description="Primary airport codes/names, or empty list if not applicable")
    train_option: Optional[TransitOption] = Field(
        default=None,
        description="Train / Rail alternative if viable (duration, train names, fare, stations)",
    )
    road_option: Optional[TransitOption] = Field(
        default=None,
        description="Road / Drive / Bus alternative if viable (duration, highway route, cab/bus fare estimate, distance)",
    )
    season_tips: Optional[str] = Field(default=None, description="Booking tips and seasonal advice")
    summary: str = Field(default="", description="Executive route and transit summary")

    @field_validator("airlines", "airports", mode="before")
    @classmethod
    def coerce_flight_lists(cls, v):
        return [] if v is None else v


# Backward compatibility alias
FlightInfo = TransitInfo


class HotelOption(BaseModel):
    """Structured accommodation recommendation emitted by Hotel Agent."""

    name: str = Field(..., description="Hotel name")
    tier: str = Field(
        default="General", description="Accommodation tier: 'Luxury', 'Boutique', 'Value', or style"
    )
    price_range: Optional[str] = Field(default=None, description="Estimated nightly rate in local or requested currency, e.g. '$150/night' or '₹10,000/night'")
    location: Optional[str] = Field(default=None, description="Neighborhood or area")
    amenities: Optional[list[str]] = Field(default_factory=list, description="Key amenities")
    description: str = Field(default="", description="Hotel summary")

    @field_validator("tier", mode="before")
    @classmethod
    def coerce_tier(cls, v):
        if not v:
            return "General"
        return str(v).strip().title()

    @field_validator("amenities", mode="before")
    @classmethod
    def coerce_amenities(cls, v):
        return [] if v is None else v


class HotelList(BaseModel):
    """Wrapper for Hotel Agent structured output."""

    hotels: Optional[list[HotelOption]] = Field(default_factory=list, description="Recommended hotel options")

    @field_validator("hotels", mode="before")
    @classmethod
    def coerce_hotels(cls, v):
        return [] if v is None else v


class ItineraryDayPlan(BaseModel):
    """Structured day schedule emitted directly by Itinerary Agent."""

    day_number: int = Field(..., description="Day index (1, 2, 3...)")
    title: str = Field(..., description="Day theme, e.g. 'Historic Asakusa & Ueno Gardens'")
    morning: Optional[str] = Field(default=None, description="Morning exploration and landmarks")
    afternoon: Optional[str] = Field(default=None, description="Afternoon cultural activity or scenic district")
    evening: Optional[str] = Field(default=None, description="Dinner recommendation or evening event")
    highlights: Optional[list[str]] = Field(default_factory=list, description="Key bulleted highlights")

    @field_validator("highlights", mode="before")
    @classmethod
    def coerce_highlights(cls, v):
        return [] if v is None else v


class ItineraryPlan(BaseModel):
    """Wrapper for Itinerary Agent structured output combining daily schedule and executive synthesis."""

    duration_days: Optional[int] = Field(default=None, description="Total days in the itinerary")
    duration_rationale: Optional[str] = Field(default=None, description="Reasoning for recommended trip duration")
    trip_summary: Optional[str] = Field(default="", description="2 clear paragraphs covering transit, daily highlights, and key activities")
    estimated_budget: Optional[str] = Field(default=None, description="Total estimated budget range per traveler in relevant currency")
    recommendations: Optional[list[str]] = Field(default_factory=list, description="3 to 4 practical travel tips")
    followup_suggestions: Optional[list[str]] = Field(
        default_factory=list,
        description="3 concrete, destination-specific follow-up prompts written strictly in the traveler's voice as first-person requests (e.g. 'What are the best street food spots in Old Delhi?', 'Add a day trip to Nara for temples and deer park', 'Switch to boutique stays under $150/night')",
    )
    days: Optional[list[ItineraryDayPlan]] = Field(default_factory=list, description="Ordered daily schedule")

    @field_validator("days", mode="before")
    @classmethod
    def coerce_days(cls, v):
        return [] if v is None else v

    @field_validator("recommendations", "followup_suggestions", mode="before")
    @classmethod
    def coerce_plan_lists(cls, v):
        return [] if v is None else v


class WeatherPlan(BaseModel):
    """Structured climate and packing recommendations."""

    timeline: Optional[str] = Field(default=None, description="The travel timeline or season evaluated")
    current_conditions: Optional[str] = Field(default=None, description="Current or timeline atmospheric conditions")
    temperature: Optional[str] = Field(default=None, description="Expected temperature range, e.g. '18°C - 24°C'")
    forecast_summary: Optional[str] = Field(default=None, description="Weather forecast overview for the trip timeline")
    packing_list: Optional[list[str]] = Field(default_factory=list, description="Recommended essentials to pack")
    source: Optional[str] = Field(default=None, description="Data source: 'openweather' or 'live_search'")

    @field_validator("packing_list", mode="before")
    @classmethod
    def coerce_packing_list(cls, v):
        return [] if v is None else v


class TripPlan(BaseModel):
    """Unified structured travel plan delivered directly to client (Zero regex required)."""

    destination_title: str = Field(..., description="Destination header")
    origin: Optional[str] = Field(default=None, description="Departure origin if specified")
    duration_label: str = Field(..., description="Duration label, e.g. '7 Days'")
    estimated_budget: Optional[str] = Field(default=None, description="Total budget estimate")
    overview_summary: str = Field(..., description="Trip overview summary")
    flights: TransitInfo = Field(default_factory=TransitInfo, description="Multi-modal transit plan across air, rail, and road")
    hotels: Optional[list[HotelOption]] = Field(default_factory=list)
    itinerary_days: Optional[list[ItineraryDayPlan]] = Field(default_factory=list)
    weather: WeatherPlan = Field(default_factory=WeatherPlan)
    recommendations: Optional[list[str]] = Field(default_factory=list)
    followup_suggestions: Optional[list[str]] = Field(default_factory=list, description="3 concrete, destination-specific follow-up prompts")

    @field_validator("hotels", "itinerary_days", "recommendations", "followup_suggestions", mode="before")
    @classmethod
    def coerce_trip_plan_lists(cls, v):
        return [] if v is None else v


class AdvisorResponse(BaseModel):
    """Structured response from the Local Advisor Agent."""

    answer: str = Field(..., description="Authentic, structured response with specific recommendations and tips in markdown format")
    followup_suggestions: Optional[list[str]] = Field(
        default_factory=list,
        description="2 to 3 concise, proactive follow-up prompts written strictly in the traveler's voice as first-person requests (e.g. 'Where can I find authentic street food near Marine Drive?', 'Add an evening street food walk to Day 2')",
    )

    @field_validator("followup_suggestions", mode="before")
    @classmethod
    def coerce_followup_suggestions(cls, v):
        return [] if v is None else v
