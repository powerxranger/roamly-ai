import {
  ParsedTripPlan,
  TravelSuccessResponse,
} from '../types';

/**
 * Direct typed mapping from backend structured TripPlan payload into UI interfaces.
 * Zero regex matching or string scraping across the entire file.
 */
export function parseTripResponse(
  query: string,
  data: TravelSuccessResponse,
  baseQuery?: string
): ParsedTripPlan {
  // Direct typed structured payload from semantic backend (ZERO regex)
  if (data.plan) {
    return {
      destinationTitle: data.plan.destination_title,
      origin: data.plan.origin || data.plan.flights.origin,
      durationLabel: data.plan.duration_label,
      estimatedBudget: data.plan.estimated_budget,
      overviewSummary: data.plan.overview_summary,
      flights: {
        origin: data.plan.flights.origin || data.plan.origin,
        destination: data.plan.flights.destination || data.plan.destination_title,
        routeType: data.plan.flights.route_type,
        primaryMode: data.plan.flights.primary_mode,
        modeRecommendation: data.plan.flights.mode_recommendation,
        departureAirport: data.plan.flights.departure_airport,
        arrivalAirport: data.plan.flights.arrival_airport,
        originToAirportTransit: data.plan.flights.origin_to_airport_transit,
        airportToDestinationTransit: data.plan.flights.airport_to_destination_transit,
        duration: data.plan.flights.duration,
        fareRange: data.plan.flights.fare_range,
        airlines: data.plan.flights.airlines,
        airports: data.plan.flights.airports,
        trainOption: data.plan.flights.train_option ? {
          mode: data.plan.flights.train_option.mode,
          duration: data.plan.flights.train_option.duration,
          fareRange: data.plan.flights.train_option.fare_range,
          operators: data.plan.flights.train_option.operators,
          terminals: data.plan.flights.train_option.terminals,
          details: data.plan.flights.train_option.details,
        } : undefined,
        roadOption: data.plan.flights.road_option ? {
          mode: data.plan.flights.road_option.mode,
          duration: data.plan.flights.road_option.duration,
          fareRange: data.plan.flights.road_option.fare_range,
          operators: data.plan.flights.road_option.operators,
          terminals: data.plan.flights.road_option.terminals,
          details: data.plan.flights.road_option.details,
        } : undefined,
        seasonTips: data.plan.flights.season_tips,
        rawText: data.plan.flights.raw_text || data.flight_results || '',
      },
      hotels: (data.plan.hotels || []).map(h => ({
        name: h.name,
        tier: h.tier,
        priceRange: h.price_range,
        location: h.location,
        amenities: h.amenities,
        description: h.description,
      })),
      itineraryDays: (data.plan.itinerary_days || []).map(d => ({
        dayNumber: d.day_number,
        title: d.title,
        morning: d.morning,
        afternoon: d.afternoon,
        evening: d.evening,
        highlights: d.highlights,
        rawText: d.raw_text || '',
      })),
      weather: {
        currentConditions: data.plan.weather.current_conditions,
        temperature: data.plan.weather.temperature,
        forecastSummary: data.plan.weather.forecast_summary,
        packingList: data.plan.weather.packing_list,
        source: data.plan.weather.source,
        rawText: data.plan.weather.raw_text || data.weather_results || '',
      },
      recommendations: data.plan.recommendations || [],
    };
  }

  // Fallback structure if backend plan payload is missing (Zero regex)
  return {
    destinationTitle: data.destination || baseQuery || query || '',
    durationLabel: '',
    overviewSummary: data.answer || '',
    flights: { rawText: data.flight_results || '' },
    hotels: [],
    itineraryDays: [],
    weather: {
      packingList: [],
      rawText: data.weather_results || '',
    },
    recommendations: [],
  };
}
