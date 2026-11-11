export interface TravelRequest {
  message: string;
  thread_id?: string | null;
}

export interface TransitOptionPayload {
  mode: string;
  duration?: string;
  fare_range?: string;
  operators?: string[];
  terminals?: string[];
  details?: string;
}

export interface TravelPlanPayload {
  destination_title: string;
  origin?: string;
  duration_label: string;
  estimated_budget?: string;
  overview_summary: string;
  flights: {
    origin?: string;
    destination?: string;
    route_type?: string;
    primary_mode?: string;
    mode_recommendation?: string;
    departure_airport?: string;
    arrival_airport?: string;
    origin_to_airport_transit?: string;
    airport_to_destination_transit?: string;
    duration?: string;
    fare_range?: string;
    airlines?: string[];
    airports?: string[];
    train_option?: TransitOptionPayload;
    road_option?: TransitOptionPayload;
    season_tips?: string;
    raw_text: string;
  };
  hotels: {
    name: string;
    tier: 'Luxury' | 'Boutique' | 'Value' | 'General';
    price_range?: string;
    location?: string;
    amenities?: string[];
    description: string;
  }[];
  itinerary_days: {
    day_number: number;
    title: string;
    morning?: string;
    afternoon?: string;
    evening?: string;
    highlights?: string[];
    raw_text: string;
  }[];
  weather: {
    current_conditions?: string;
    temperature?: string;
    forecast_summary?: string;
    packing_list: string[];
    source?: string;
    raw_text: string;
  };
  recommendations: string[];
}

export interface TravelSuccessResponse {
  success: true;
  thread_id: string;
  response_type?: 'plan' | 'conversation';
  answer: string;
  plan?: TravelPlanPayload;
  destination?: string;
  flight_results: string;
  hotel_results: string;
  weather_results: string;
  itinerary: string;
  llm_calls: number;
}

export interface TravelErrorResponse {
  success: false;
  error: string;
  raw_error?: string;
  missing?: string[];
}

export type TravelResponse = TravelSuccessResponse | TravelErrorResponse;

export interface HealthResponse {
  status: string;
  message: string;
  ready: boolean;
  missing: string[];
}

export type PlannerTaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export interface PlannerTask {
  id: string;
  label: string;
  sublabel: string;
  icon: 'flight' | 'hotel' | 'weather' | 'itinerary' | 'synthesis';
  status: PlannerTaskStatus;
  technicalRole: string;
}

export type ActiveTab = 'overview' | 'itinerary' | 'flights' | 'hotels' | 'weather';

export interface ParsedTransitOption {
  mode: string;
  duration?: string;
  fareRange?: string;
  operators?: string[];
  terminals?: string[];
  details?: string;
}

// Parsed UI Data Structures
export interface ParsedFlightInfo {
  origin?: string;
  destination?: string;
  routeType?: string;
  primaryMode?: string;
  modeRecommendation?: string;
  departureAirport?: string;
  arrivalAirport?: string;
  originToAirportTransit?: string;
  airportToDestinationTransit?: string;
  airports?: string[];
  airlines?: string[];
  duration?: string;
  fareRange?: string;
  trainOption?: ParsedTransitOption;
  roadOption?: ParsedTransitOption;
  seasonTips?: string;
  rawText: string;
}

// Multi-modal transit type aliases
export type ParsedTransitInfo = ParsedFlightInfo;
export type TransitPlanPayload = TravelPlanPayload['flights'];

export interface ParsedHotelItem {
  name: string;
  tier: 'Luxury' | 'Boutique' | 'Value' | 'General';
  priceRange?: string;
  location?: string;
  amenities?: string[];
  description: string;
}

export interface ParsedItineraryDay {
  dayNumber: number;
  title: string;
  morning?: string;
  afternoon?: string;
  evening?: string;
  highlights?: string[];
  rawText: string;
}

export interface ParsedWeatherInfo {
  currentConditions?: string;
  temperature?: string;
  forecastSummary?: string;
  packingList: string[];
  source?: string;
  rawText: string;
}

export interface ParsedTripPlan {
  destinationTitle: string;
  origin?: string;
  durationLabel: string;
  estimatedBudget?: string;
  overviewSummary: string;
  flights: ParsedFlightInfo;
  hotels: ParsedHotelItem[];
  itineraryDays: ParsedItineraryDay[];
  weather: ParsedWeatherInfo;
  recommendations: string[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  data?: TravelSuccessResponse;
  timestamp: Date;
}
