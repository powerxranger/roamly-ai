"""Unit tests verifying zero-regex, schema-driven Pydantic architecture."""

import unittest
from src.models.travel_models import (
    FlightInfo,
    HotelOption,
    ItineraryDayPlan,
    TransitInfo,
    TransitOption,
    TravelIntent,
    TripPlan,
    WeatherPlan,
)
from src.utils.plan_builder import assemble_trip_plan


class TestPydanticArchitecture(unittest.TestCase):
    def test_travel_intent_validation(self):
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
        self.assertEqual(intent.intent_type, "initial_planning")
        self.assertEqual(intent.destination, "Kyoto & Tokyo, Japan")
        self.assertEqual(intent.primary_city, "Kyoto")
        self.assertEqual(intent.duration_days, 7)
        self.assertTrue(intent.needs_flights)
        self.assertTrue(intent.needs_hotels)
        self.assertTrue(intent.needs_weather)
        self.assertTrue(intent.needs_itinerary)

    def test_travel_intent_unspecified_duration(self):
        data = {
            "intent_type": "initial_planning",
            "destination": "Amsterdam",
            "primary_city": "Amsterdam",
            "needs_itinerary": True,
        }
        intent = TravelIntent(**data)
        self.assertIsNone(intent.duration_days)
        self.assertEqual(intent.destination, "Amsterdam")

    def test_assemble_trip_plan_zero_regex(self):
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

        self.assertEqual(plan_dict["destination_title"], "Kyoto, Japan")
        self.assertEqual(len(plan_dict["hotels"]), 1)
        self.assertEqual(plan_dict["hotels"][0]["name"], "The Ritz-Carlton Kyoto")
        self.assertEqual(plan_dict["hotels"][0]["price_range"], "₹65,000/night")
        self.assertEqual(len(plan_dict["itinerary_days"]), 1)
        self.assertEqual(plan_dict["itinerary_days"][0]["day_number"], 1)
        self.assertEqual(plan_dict["weather"]["temperature"], "22°C")
        self.assertEqual(plan_dict["flights"]["airlines"], ["ANA", "JAL"])
        self.assertEqual(plan_dict["flights"]["fare_range"], "₹75,000 - ₹95,000")

    def test_multimodal_flight_info_assembly(self):
        flight_data = {
            "origin": "Rishikesh",
            "destination": "Hampi",
            "route_type": "Multi-modal (Road/Rail + Flight)",
            "departure_airport": "Dehradun Jolly Grant Airport (DED)",
            "origin_to_airport_transit": "Taxi from Rishikesh to Dehradun Airport (~35 km, 45 mins)",
            "arrival_airport": "Hubli Airport (HBX)",
            "airport_to_destination_transit": "Cab or train from Hubli to Hampi (~140 km, 3 hours)",
            "duration": "4h 30m with 1 stop",
            "fare_range": "₹9,000 - ₹15,000",
            "airlines": ["IndiGo"],
            "airports": ["DED", "HBX"],
            "season_tips": "Book cabs in advance",
            "summary": "Multi-modal route combining road transfers and connecting flights.",
        }

        plan_dict = assemble_trip_plan(
            destination="Hampi",
            origin="Rishikesh",
            overview_summary="Multi-modal travel from Rishikesh to Hampi.",
            estimated_budget="₹35,000 - ₹50,000",
            recommendations=["Reserve local transfers early"],
            flight_data=flight_data,
        )

        flights = plan_dict["flights"]
        self.assertEqual(flights["route_type"], "Multi-modal (Road/Rail + Flight)")
        self.assertEqual(flights["departure_airport"], "Dehradun Jolly Grant Airport (DED)")
        self.assertEqual(flights["origin_to_airport_transit"], "Taxi from Rishikesh to Dehradun Airport (~35 km, 45 mins)")
        self.assertEqual(flights["arrival_airport"], "Hubli Airport (HBX)")
        self.assertEqual(flights["airport_to_destination_transit"], "Cab or train from Hubli to Hampi (~140 km, 3 hours)")

    def test_regional_transit_train_and_road_comparison(self):
        flight_data = {
            "origin": "Delhi",
            "destination": "Jaipur",
            "route_type": "Short Regional Route",
            "primary_mode": "Train",
            "mode_recommendation": "Vande Bharat Express is recommended over flights for this 270 km trip because center-to-center travel takes under 4 hours without airport security delays.",
            "duration": None,
            "fare_range": None,
            "airlines": [],
            "airports": [],
            "train_option": {
                "mode": "Train",
                "duration": "3h 45m",
                "fare_range": "₹900 - ₹1,800",
                "operators": ["Vande Bharat Express", "Shatabdi Express"],
                "terminals": ["New Delhi (NDLS)", "Jaipur (JP)"],
                "details": "Multiple daily express trains departing central New Delhi.",
            },
            "road_option": {
                "mode": "Road / Drive",
                "duration": "4h 30m",
                "fare_range": "₹3,500 - ₹5,000 for cab",
                "operators": ["NH 48", "Delhi-Jaipur Expressway"],
                "terminals": ["Delhi", "Jaipur"],
                "details": "270 km highway drive via the express corridor.",
            },
            "season_tips": "Book morning train seats 1-2 weeks in advance.",
            "summary": "Train is the most efficient choice between Delhi and Jaipur.",
        }

        plan_dict = assemble_trip_plan(
            destination="Jaipur",
            origin="Delhi",
            overview_summary="Regional trip from Delhi to Jaipur.",
            estimated_budget="₹15,000 - ₹25,000",
            recommendations=["Take the morning Vande Bharat train"],
            flight_data=flight_data,
        )

        flights = plan_dict["flights"]
        self.assertEqual(flights["primary_mode"], "Train")
        self.assertIn("Vande Bharat", flights["mode_recommendation"])
        self.assertIsNotNone(flights["train_option"])
        self.assertEqual(flights["train_option"]["duration"], "3h 45m")
        self.assertEqual(flights["train_option"]["fare_range"], "₹900 - ₹1,800")
        self.assertIsNotNone(flights["road_option"])
        self.assertEqual(flights["road_option"]["duration"], "4h 30m")

    def test_regional_transit_null_airlines_and_airports_coercion(self):
        """Verify that when an LLM returns null for airlines or airports on regional routes,
        Pydantic cleanly coerces them to empty lists and generates schema allowing null."""
        flight_data = {
            "origin": "Faridabad",
            "destination": "Mathura",
            "route_type": "Short Regional Route",
            "primary_mode": "Train",
            "mode_recommendation": "For the 140 km Faridabad-Mathura corridor, rail is the fastest option.",
            "duration": None,
            "fare_range": None,
            "airlines": None,  # Simulated Groq LLM tool output when flight is not viable
            "airports": None,  # Simulated Groq LLM tool output
            "train_option": {
                "mode": "Train",
                "duration": "2h 30m",
                "fare_range": "₹250 - ₹800",
                "operators": None,
                "terminals": None,
                "details": "Frequent daily trains.",
            },
            "road_option": None,
            "season_tips": "Book early.",
            "summary": "Faridabad to Mathura is best by train.",
        }

        # Direct model parsing
        model = FlightInfo(**flight_data)
        self.assertEqual(model.airlines, [])
        self.assertEqual(model.airports, [])
        self.assertIsNotNone(model.train_option)
        self.assertEqual(model.train_option.operators, [])
        self.assertEqual(model.train_option.terminals, [])

        # Schema verification: anyOf should allow null so Groq tool validator never rejects tool call
        schema = FlightInfo.model_json_schema()
        airlines_schema = schema["properties"]["airlines"]
        self.assertIn("anyOf", airlines_schema)
        allowed_types = [branch.get("type") for branch in airlines_schema["anyOf"]]
        self.assertIn("null", allowed_types)
        self.assertIn("array", allowed_types)

        # Plan assembly verification
        plan_dict = assemble_trip_plan(
            destination="Mathura",
            origin="Faridabad",
            overview_summary="Trip to Mathura.",
            flight_data=flight_data,
        )
        self.assertEqual(plan_dict["flights"]["airlines"], [])
        self.assertEqual(plan_dict["flights"]["airports"], [])
        self.assertEqual(plan_dict["flights"]["primary_mode"], "Train")

    def test_ground_route_suppresses_flight_legs_and_airports(self):
        """Verify that pure ground routes (Road / Drive, Train) have null flight duration,
        no airport legs, and assemble into a clean ground-only plan."""
        flight_data = {
            "origin": "Rishikesh",
            "destination": "Haridwar",
            "route_type": "Short Regional Route",
            "primary_mode": "Road / Drive",
            "mode_recommendation": "Direct road travel via NH 334 takes roughly 45 minutes for this 25 km trip.",
            "duration": None,
            "fare_range": None,
            "airlines": [],
            "airports": [],
            "departure_airport": None,
            "arrival_airport": None,
            "origin_to_airport_transit": None,
            "airport_to_destination_transit": None,
            "road_option": {
                "mode": "Road / Drive",
                "duration": "45 mins",
                "fare_range": "₹500 - ₹900",
                "operators": ["Auto / Cab", "Local Bus"],
                "terminals": ["Rishikesh", "Haridwar"],
                "details": "Direct highway drive along NH 334.",
            },
            "season_tips": "Avoid peak ghat pilgrimage hours.",
            "summary": "Road transit is the natural and fastest choice between Rishikesh and Haridwar.",
        }

        plan_dict = assemble_trip_plan(
            destination="Haridwar",
            origin="Rishikesh",
            overview_summary="Road trip from Rishikesh to Haridwar.",
            flight_data=flight_data,
        )

        flights = plan_dict["flights"]
        self.assertEqual(flights["primary_mode"], "Road / Drive")
        self.assertIsNone(flights["duration"])
        self.assertIsNone(flights["departure_airport"])
        self.assertIsNone(flights["arrival_airport"])
        self.assertIsNone(flights["origin_to_airport_transit"])
        self.assertIsNone(flights["airport_to_destination_transit"])
        self.assertIsNotNone(flights["road_option"])
        self.assertEqual(flights["road_option"]["duration"], "45 mins")

    def test_transit_info_model_naming_and_compatibility(self):
        """Verify that TransitInfo and FlightInfo are interchangeable."""
        self.assertIs(TransitInfo, FlightInfo)
        info = TransitInfo(
            primary_mode="Train",
            mode_recommendation="High speed rail is optimal.",
            train_option=TransitOption(mode="Train", duration="2h", fare_range="₹800"),
        )
        self.assertEqual(info.primary_mode, "Train")
        self.assertEqual(info.airlines, [])
        self.assertEqual(info.airports, [])
        self.assertEqual(info.train_option.operators, [])

    def test_travel_intent_general_question(self):
        """Verify that follow-up questions (e.g. food, spots, tips) produce valid general_question intent with needs_itinerary=False."""
        data = {
            "intent_type": "general_question",
            "destination": "Mumbai",
            "needs_flights": False,
            "needs_hotels": False,
            "needs_weather": False,
            "needs_itinerary": False,
            "refinement_summary": "Looking for the best Vadapav spots in Mumbai",
        }
        intent = TravelIntent(**data)
        self.assertEqual(intent.intent_type, "general_question")
        self.assertEqual(intent.destination, "Mumbai")
        self.assertFalse(intent.needs_itinerary)
        self.assertFalse(intent.needs_flights)
        self.assertFalse(intent.needs_hotels)

    def test_dynamic_supervisor_routing_logic(self):
        """Verify that route_supervisor dynamically selects execution paths based on classified intent."""
        from src.graph.graph import route_supervisor

        # Path 3: Q&A / recommendations -> fast advisor agent
        qa_state = {
            "intent": {"intent_type": "general_question"},
            "destination": "Mumbai",
            "user_query": "What are the best Vadapav places?",
        }
        self.assertEqual(route_supervisor(qa_state), "advisor_agent")

        # Path 1: Initial trip planning -> scout fan-out
        initial_state = {
            "intent": {"intent_type": "initial_planning"},
            "destination": "Tokyo",
            "user_query": "Plan a 7-day trip to Tokyo",
        }
        self.assertEqual(route_supervisor(initial_state), "scout_fanout")

        # Path 2: Itinerary modification -> scout fan-out (surgical delta execution)
        modify_state = {
            "intent": {"intent_type": "refine_itinerary"},
            "destination": "Mumbai",
            "user_query": "Add a day trip to Alibaug on Day 3",
        }
        self.assertEqual(route_supervisor(modify_state), "scout_fanout")

    def test_graph_structure_and_compilation(self):
        """Verify that the StateGraph compiles cleanly with dynamic conditional routing and checkpointer."""
        from src.graph.graph import build_graph, get_travel_graph

        uncompiled = build_graph()
        self.assertIn("router_agent", uncompiled.nodes)
        self.assertIn("guardrail_agent", uncompiled.nodes)
        self.assertIn("advisor_agent", uncompiled.nodes)
        self.assertIn("scout_fanout", uncompiled.nodes)
        self.assertIn("flight_agent", uncompiled.nodes)
        self.assertIn("hotel_agent", uncompiled.nodes)
        self.assertIn("weather_agent", uncompiled.nodes)
        self.assertIn("itinerary_agent", uncompiled.nodes)
        self.assertIn("final_agent", uncompiled.nodes)

        compiled = get_travel_graph()
        self.assertIsNotNone(compiled)

    def test_guardrail_out_of_scope_intent_and_routing(self):
        """Verify out_of_scope queries short-circuit to guardrail_agent without planning fanout."""
        from src.graph.graph import route_supervisor

        data = {
            "intent_type": "out_of_scope",
            "destination": "",
            "needs_flights": False,
            "needs_hotels": False,
            "needs_weather": False,
            "needs_itinerary": False,
            "guardrail_message": "Roamly specializes in travel planning.",
        }
        intent = TravelIntent(**data)
        self.assertEqual(intent.intent_type, "out_of_scope")
        self.assertFalse(intent.needs_flights)
        self.assertFalse(intent.needs_itinerary)

        state = {
            "intent": intent.model_dump(),
            "user_query": "Write a python script to invert a binary tree",
        }
        self.assertEqual(route_supervisor(state), "guardrail_agent")

    def test_guardrail_clarification_needed_intent_and_routing(self):
        """Verify vague travel queries without a destination route to guardrail_agent."""
        from src.graph.graph import route_supervisor

        data = {
            "intent_type": "clarification_needed",
            "destination": "",
            "needs_flights": False,
            "needs_hotels": False,
            "needs_weather": False,
            "needs_itinerary": False,
            "refinement_summary": "User wants a weekend trip but did not specify destination",
        }
        intent = TravelIntent(**data)
        self.assertEqual(intent.intent_type, "clarification_needed")

        state = {
            "intent": intent.model_dump(),
            "user_query": "I want to go on a trip with my friends next weekend",
        }
        self.assertEqual(route_supervisor(state), "guardrail_agent")

    def test_guardrail_agent_execution(self):
        """Verify guardrail_agent returns conversational response without invoking LLM."""
        from src.agents.guardrail_agent import guardrail_agent

        state = {
            "intent": {
                "intent_type": "out_of_scope",
                "guardrail_message": "Roamly is dedicated exclusively to travel planning.",
            },
            "user_query": "Can you do my calculus homework?",
        }
        result = guardrail_agent(state)
        self.assertEqual(result["response_type"], "conversation")
        self.assertIn("Roamly is dedicated exclusively", result["messages"][0].content)

    def test_guardrail_agent_dynamic_fallback(self):
        """Verify guardrail_agent dynamically invokes LLM with zero hardcoded branches."""
        from unittest.mock import MagicMock, patch
        from src.agents.guardrail_agent import guardrail_agent

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "I specialize in travel planning. Try exploring 5 days in Tokyo!"
        mock_llm.invoke.return_value = mock_response

        state = {
            "intent": {
                "intent_type": "out_of_scope",
                "guardrail_message": None,
            },
            "user_query": "Write a python function to compute fibonacci numbers",
            "llm_calls": 1,
        }

        with patch("src.agents.guardrail_agent.get_llm", return_value=mock_llm):
            result = guardrail_agent(state)

        self.assertEqual(result["response_type"], "conversation")
        self.assertIn("Tokyo", result["messages"][0].content)
        self.assertEqual(result["llm_calls"], 2)

    def test_international_trip_plan_assembly(self):
        """Verify that assemble_trip_plan cleanly handles international trips with non-INR currencies."""
        flight_data = {
            "origin": "London",
            "destination": "Paris",
            "route_type": "Short Regional Route",
            "primary_mode": "Train",
            "mode_recommendation": "Eurostar high-speed rail from St Pancras to Gare du Nord is faster and more convenient than flying.",
            "duration": None,
            "fare_range": None,
            "airlines": [],
            "airports": [],
            "train_option": {
                "mode": "Train",
                "duration": "2h 16m",
                "fare_range": "€78 - €140",
                "operators": ["Eurostar"],
                "terminals": ["London St Pancras", "Paris Gare du Nord"],
                "details": "Direct high-speed rail under the English Channel.",
            },
            "road_option": None,
            "season_tips": "Book Eurostar at least 4 weeks ahead for best fares.",
            "summary": "Eurostar is the optimal direct transit between London and Paris.",
        }
        hotel_data = [
            {
                "name": "Hotel Monge",
                "tier": "Boutique",
                "price_range": "€220 - €310/night",
                "location": "Latin Quarter, 5th Arrondissement",
                "amenities": ["Spa", "Tea Salon", "Courtyard"],
                "description": "Charming boutique hotel in the historic Latin Quarter.",
            }
        ]
        itinerary_data = [
            {
                "day_number": 1,
                "title": "Arrival and Latin Quarter Discovery",
                "morning": "Eurostar arrival at Gare du Nord and check-in",
                "afternoon": "Stroll Jardin des Plantes and Pantheon",
                "evening": "Bistro dinner along Rue Mouffetard",
                "highlights": ["Latin Quarter", "Jardin des Plantes"],
            }
        ]
        weather_data = {
            "current_conditions": "Partly cloudy",
            "temperature": "16°C - 21°C",
            "forecast_summary": "Mild spring weather with occasional light showers.",
            "packing_list": ["Light trench coat", "Comfortable walking shoes", "Compact umbrella"],
        }

        plan_dict = assemble_trip_plan(
            destination="Paris, France",
            origin="London, UK",
            overview_summary="High-speed rail journey from London to Paris.",
            estimated_budget="€850 - €1,250",
            recommendations=["Reserve Eurostar early", "Get Paris Museum Pass"],
            flight_data=flight_data,
            hotel_data=hotel_data,
            itinerary_data=itinerary_data,
            weather_data=weather_data,
            duration_days=3,
        )

        self.assertEqual(plan_dict["destination_title"], "Paris, France")
        self.assertEqual(plan_dict["estimated_budget"], "€850 - €1,250")
        self.assertEqual(plan_dict["hotels"][0]["price_range"], "€220 - €310/night")
        self.assertEqual(plan_dict["flights"]["train_option"]["fare_range"], "€78 - €140")
        self.assertEqual(plan_dict["flights"]["primary_mode"], "Train")

    def test_proactive_refinement_levers_in_trip_plan(self):
        """Verify assemble_trip_plan preserves proactive refinement prompts for traveler customization."""
        prompts = [
            "Extend to 4 days to include a day trip to Versailles",
            "Switch to boutique stays in Saint-Germain under €180",
            "Make Day 2 more relaxed with evening Seine cruise",
        ]
        plan_dict = assemble_trip_plan(
            destination="Paris",
            overview_summary="Customizable 3-day Paris trip.",
            refinement_prompts=prompts,
        )
        self.assertEqual(len(plan_dict["refinement_prompts"]), 3)
        self.assertIn("Versailles", plan_dict["refinement_prompts"][0])


if __name__ == "__main__":
    unittest.main()
