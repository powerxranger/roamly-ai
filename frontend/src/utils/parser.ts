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
      durationLabel: data.plan.duration_label,
      estimatedBudget: data.plan.estimated_budget,
      overviewSummary: data.plan.overview_summary,
      flights: {
        duration: data.plan.flights.duration,
        fareRange: data.plan.flights.fare_range,
        airlines: data.plan.flights.airlines,
        airports: data.plan.flights.airports,
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
        rawText: data.plan.weather.raw_text || data.weather_results || '',
      },
      recommendations: data.plan.recommendations || [],
    };
  }

  // Default fallback if backend plan payload is somehow missing (Zero regex)
  return {
    destinationTitle: data.destination || baseQuery || query || 'Custom Trip',
    durationLabel: '7 Days',
    overviewSummary: data.answer || 'Travel plan generated for your trip.',
    flights: { rawText: data.flight_results || '' },
    hotels: [],
    itineraryDays: [],
    weather: {
      packingList: ['Comfortable walking shoes', 'Universal power adapter', 'Weather-appropriate layers'],
      rawText: data.weather_results || '',
    },
    recommendations: [],
  };
}
