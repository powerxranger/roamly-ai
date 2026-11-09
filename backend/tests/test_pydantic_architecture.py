"""Unit tests verifying zero-regex, schema-driven Pydantic architecture."""

import unittest
from src.models.travel_models import (
    FlightInfo,
    HotelOption,
    ItineraryDayPlan,
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


if __name__ == "__main__":
    unittest.main()
