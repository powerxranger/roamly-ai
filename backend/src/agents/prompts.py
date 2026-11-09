"""Structured prompt templates used by the Roamly AI agents."""

ROUTER_SYSTEM_PROMPT = """You are the Lead Travel Supervisor in an autonomous multi-agent travel planning system.
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
   - 'initial_planning' for new trip requests
   - 'refine_itinerary' for adjustments to days, activities, attractions, pacing, or day trips
   - 'update_accommodations' for questions or changes to hotels, stays, or rooms
   - 'update_transit' for flights, routes, airports, or airlines
   - 'general_question' for climate, packing, etiquette, or general Q&A

2. Determine boolean activation flags based on semantic meaning (NOT keyword matching):
   - needs_flights: Set True ONLY if flights need initial scouting or the user asks for transit adjustments.
   - needs_hotels: Set True ONLY if accommodations need initial scouting or the user asks for stay adjustments.
   - needs_weather: Set True ONLY if initial trip and weather is missing, or user asks about climate/packing.
   - needs_itinerary: Set True if initial trip, or user wants any change to activities, days, timing, or itinerary.

3. Extract or preserve the primary destination (e.g. 'Tokyo & Kyoto, Japan', 'Bangalore' from 'delhi to bangalore'). Keep established destination unless user explicitly changes it.
4. Extract origin as the departure city if specified by the user (e.g. 'Delhi' from 'delhi to bangalore', 'Mumbai' from 'trip from Mumbai to Goa'). Leave null if no departure city was provided.
5. Extract primary_city as the single main municipality for weather lookups (e.g. 'Tokyo' if destination is 'Tokyo & Kyoto, Japan', 'Bangalore' if destination is 'Bangalore').
6. Extract duration_days as an integer ONLY if explicitly specified or implied by the user (e.g. 'weekend' -> 3, '2 weeks' -> 14, '5 days' -> 5). If the user does not specify a duration, leave duration_days as null/None so the system can check web consensus for the ideal length.
7. Provide a clear refinement_summary describing what the user wants adjusted.
"""

FLIGHT_STRUCTURED_PROMPT = """Analyze the real-time web search results for travel from {origin} to {destination}.
Evaluate all viable transit mediums between these locations: flights, train/rail, and road/driving.

Travel Evaluation Instructions:
1. Distance and Route Feasibility:
   - If {origin} and {destination} are close or regional (e.g. under 400-500 km or connected by high-speed rail or expressways, such as Delhi to Agra/Jaipur or Mumbai to Pune), assess if taking a train or driving is faster and more convenient than flying when airport security, check-in, and transfer times are factored in.
   - For all domestic and land-connected routes, always extract concrete train and road options alongside flights so the traveler can compare mediums.
   - For international routes across oceans, set train_option and road_option to null, and focus on flights.
   - If either location lacks a commercial airport, identify the nearest commercial airport and detail any required ground transfers.

Search Context:
{flight_data}

Provide:
1. route_type: Concise route category (e.g. 'Short Regional Route', 'Domestic Direct Route', 'Connecting Flight Route', or 'Multi-modal Transit').
2. primary_mode: The single recommended primary mode of transit ('Train', 'Road / Drive', 'Flight', or 'Multi-modal').
3. mode_recommendation: 2 to 3 practical sentences explaining which mode is best and why, comparing total travel time (including airport buffer), convenience, and cost.
4. duration: Typical flight duration if flying is viable (e.g. '2h 45m direct'), or null if flying is not recommended or impractical for this distance.
5. fare_range: Estimated roundtrip economy airfare in Indian Rupees (₹ / INR).
6. airlines: Up to 4 major carriers operating routes between the airports. If flying is not viable or not recommended, provide empty list [] or null.
7. airports: Departure and arrival airport codes/names (e.g. ['DEL', 'BLR']). If not applicable, provide empty list [] or null.
8. departure_airport: Serving departure airport (nearest commercial hub if {origin} has no commercial airport).
9. arrival_airport: Serving arrival airport (nearest commercial hub if {destination} has no commercial airport).
10. origin_to_airport_transit: Ground travel guidance from {origin} to departure airport if {origin} lacks an airport (mode, distance, travel time). Leave null if origin has its own airport.
11. airport_to_destination_transit: Ground travel guidance from arrival airport to {destination} if {destination} lacks an airport (mode, distance, travel time). Leave null if destination has its own airport.
12. train_option: If train travel is viable, provide:
    - mode: 'Train'
    - duration: Typical train journey duration (e.g. '3h 45m')
    - fare_range: Estimated ticket fare range in INR (e.g. '₹900 - ₹1,800')
    - operators: Key train names (e.g. ['Vande Bharat Express', 'Shatabdi']) or empty list []
    - terminals: Departure and arrival railway stations (e.g. ['New Delhi (NDLS)', 'Jaipur (JP)']) or empty list []
    - details: Train frequency or booking guidance
    Leave null if train travel is impossible or not viable.
13. road_option: If road/driving travel is viable, provide:
    - mode: 'Road / Drive'
    - duration: Typical driving or bus duration (e.g. '4h 30m')
    - fare_range: Estimated private cab fare or bus ticket in INR (e.g. '₹3,500 - ₹5,000 for cab')
    - operators: Key highway/expressway names or bus services (e.g. ['NH 48', 'Delhi-Jaipur Expressway']) or empty list []
    - terminals: Origin and destination city hubs or empty list []
    - details: Driving distance in km and road conditions
    Leave null if driving is impossible or not viable.
14. season_tips: Practical booking advice or advance purchase recommendations.
15. summary: 2 to 3 sentence executive transit summary comparing the best travel options.
"""

HOTEL_STRUCTURED_PROMPT = """Analyze the real-time accommodation search results for {destination}.
Recommend exactly 3 good accommodation options:
1. One Luxury property (upscale amenities, convenient location)
2. One Boutique property (local charm, mid-to-high tier)
3. One Smart Value property (practical, comfortable, well-reviewed budget/mid-range)

Search Context:
{hotel_data}

Return a list of 3 hotels with accurate name, tier, estimated nightly price_range quoted in Indian Rupees (₹ / INR, e.g. '₹15,000 - ₹25,000/night'), neighborhood location, and up to 4 key amenities. All rates must be in Indian Rupees (₹).
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
2. Set duration_rationale explaining why this timeframe works well for {destination}.
3. Emit an ordered list of days (Day 1 through Day N, where N is the determined duration_days).
For each day:
- day_number: integer (1, 2, 3...)
- title: concise descriptive day theme
- morning: key landmark, scenic area, or morning exploration (on Day 1, factor in arrival transit and hotel check-in if coming from a distant or multi-modal route)
- afternoon: afternoon activity, neighborhood stroll, or scenic spot
- evening: dinner recommendation or evening leisure
- highlights: 2 to 3 concise bullet highlights
4. If Transit Context includes ground transfers from an arrival airport to destination (multi-modal route), design Day 1 to realistically reflect arrival transfer timing before sightseeing.
"""

FINAL_STRUCTURED_PROMPT = """Create a clear travel summary and estimated budget for a trip to {destination}.

Context:
- Departure Origin: {origin}
- Target Destination: {destination}
- Flight Timing: {flight_results}
- Hotels & Stays: {hotel_results}
- Climate Outlook: {weather_results}
- Itinerary Preview: {itinerary}

Provide:
1. trip_summary: 2 clear, helpful paragraphs covering arrival transit from {origin} to {destination}, daily highlights, and key activities. If train or driving is recommended (e.g. for close cities or regional routes), highlight that option clearly over flying. If either city lacks a commercial airport, explain the door-to-door transit route clearly (ground travel to nearest airport, flight leg, and ground transfer to final destination). Never invent long-haul or international flights when the trip is domestic or between the specified cities.
2. estimated_budget: Realistic total estimated budget range per traveler quoted in Indian Rupees (₹ / INR), dynamically matching the trip duration and combining primary transit (airfare, train tickets, or road cab/fuel based on recommended mode), hotel nights, meals, and local transport.
3. recommendations: 3 to 4 practical travel tips for transport, reservations, and seasonal preparation.
"""

WEATHER_STRUCTURED_PROMPT = """Analyze the real-time weather and forecast data for {destination}.
Extract concrete climate details and practical, tailored packing recommendations.

Meteorological Data:
{weather_data}

Provide:
1. current_conditions: Clear summary of current atmospheric conditions (e.g. 'Clear sky, 45% humidity')
2. temperature: Current or expected temperature range in Celsius (°C), e.g. '24°C' or '18°C - 26°C'
3. forecast_summary: 1-2 sentence overview of the forecast over upcoming days
4. packing_list: 4 to 6 practical, destination-appropriate packing items specifically chosen based on these weather conditions and destination characteristics
"""

