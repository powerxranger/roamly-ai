"""Structured prompt templates used by the Roamly AI agents."""

ROUTER_SYSTEM_PROMPT = """You are the Lead Travel Supervisor in an autonomous multi-agent concierge system.
Analyze the user's travel request semantically to determine the required agent activations.

Existing Trip State:
- Established Destination: {existing_destination}
- Existing Flights Planned: {has_flights}
- Existing Hotels Planned: {has_hotels}
- Existing Itinerary Planned: {has_itinerary}

Query:
{user_query}

Instructions:
1. Determine the intent_type:
   - 'initial_planning' for new journey requests
   - 'refine_itinerary' for adjustments to days, activities, attractions, pacing, or day trips
   - 'update_accommodations' for questions or changes to hotels, stays, or rooms
   - 'update_transit' for flights, routes, airports, or airlines
   - 'general_question' for climate, packing, etiquette, or general Q&A

2. Determine boolean activation flags based on semantic meaning (NOT keyword matching):
   - needs_flights: Set True ONLY if flights need initial scouting or the user asks for transit adjustments.
   - needs_hotels: Set True ONLY if accommodations need initial scouting or the user asks for stay adjustments.
   - needs_weather: Set True ONLY if initial trip and weather is missing, or user asks about climate/packing.
   - needs_itinerary: Set True if initial trip, or user wants any change to activities, days, timing, or itinerary.

3. Extract or preserve the primary destination (e.g. 'Tokyo & Kyoto, Japan'). Keep established destination unless user explicitly changes it.
4. Extract primary_city as the single main municipality for weather lookups (e.g. 'Tokyo' if destination is 'Tokyo & Kyoto, Japan').
5. Extract duration_days as an integer ONLY if explicitly specified or implied by the user (e.g. 'weekend' -> 3, '2 weeks' -> 14, '5 days' -> 5). If the user does not specify a duration, leave duration_days as null/None so the concierge can scout web consensus for the ideal length.
6. Provide a clear refinement_summary describing what the user wants adjusted.
"""

FLIGHT_STRUCTURED_PROMPT = """Analyze the real-time web search results for travel to {destination}.
Extract concrete, structured flight intelligence.

Search Context:
{flight_data}

Provide:
1. duration: Realistic flight duration, e.g. '11-13 hours direct'
2. fare_range: Estimated roundtrip coach/economy fare range, e.g. '$850 - $1,250'
3. airlines: Up to 4 major carriers operating routes to this destination
4. airports: Departure/arrival hub codes or names (e.g. ['HND', 'NRT'])
5. season_tips: Key booking advice or peak season warning
6. summary: 2-sentence executive summary of the flight landscape
"""

HOTEL_STRUCTURED_PROMPT = """Analyze the real-time accommodation search results for {destination}.
Curate exactly 3 standout accommodation recommendations:
1. One Luxury property (5-star, top amenities, upscale location)
2. One Boutique property (charming neighborhood, character, mid-to-high tier)
3. One Smart Value property (practical, great transit access, well-reviewed budget/mid-range)

Search Context:
{hotel_data}

Return a list of 3 hotels with accurate name, tier, estimated nightly price_range, neighborhood location, and up to 4 key amenities.
"""

ITINERARY_STRUCTURED_PROMPT = """Create or refine a structured day-by-day travel itinerary for {destination}.

Trip Parameters:
- User-Specified Duration: {requested_duration}
- Web Search Consensus on Recommended Trip Length:
{duration_context}
- Transit Context: {flight_results}
- Accommodation Context: {hotel_results}
- Climate Forecast: {weather_results}

Refinement Context (if modifying existing schedule):
{refinement_context}

Instructions:
1. Determine duration_days:
   - If User-Specified Duration is provided, use that exact count.
   - Otherwise, adopt the travel consensus from the Web Search (typically between 3 and 10 days to ensure full coverage without filler).
2. Set duration_rationale explaining why this timeframe is optimal for {destination}.
3. Emit an ordered list of days (Day 1 through Day {duration_days}).
For each day:
- day_number: integer (1, 2, 3...)
- title: concise descriptive day theme
- morning: key landmark, scenic area, or morning exploration
- afternoon: afternoon cultural activity, neighborhood stroll, or scenic spot
- evening: curated dinner recommendation or evening leisure
- highlights: 2 to 3 concise bullet highlights
"""

FINAL_STRUCTURED_PROMPT = """Synthesize an executive travel overview and budget for a trip to {destination}.

Context:
- Flight Timing: {flight_results}
- Stays & Sanctuaries: {hotel_results}
- Climate Outlook: {weather_results}
- Itinerary Preview: {itinerary}

Provide:
1. trip_summary: 2 vivid, polished paragraphs capturing the atmosphere, highlights, and best travel window.
2. estimated_budget: Total estimated budget range per traveler (e.g. '$3,500 - $4,800 per person total').
3. recommendations: 3 to 4 essential insider concierge tips for transport, reservations, and seasonal preparation.
"""
