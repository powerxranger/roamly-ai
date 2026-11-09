export interface TravelRequest {
  message: string;
  thread_id?: string | null;
}

export interface TravelPlanPayload {
  destination_title: string;
  duration_label: string;
  estimated_budget?: string;
  overview_summary: string;
  flights: {
    duration?: string;
    fare_range?: string;
    airlines?: string[];
    airports?: string[];
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

// Backward compatibility alias
export type ConciergeTask = PlannerTask;
export type ConciergeTaskStatus = PlannerTaskStatus;

export interface AgentProgress {
  id: string;
  label: string;
  role: string;
  category: 'parallel' | 'sequential';
  status: 'pending' | 'running' | 'completed' | 'failed';
}

export type ActiveTab = 'overview' | 'itinerary' | 'flights' | 'hotels' | 'weather' | 'dossier';

// Parsed UI Data Structures
export interface ParsedFlightInfo {
  airports?: string[];
  airlines?: string[];
  duration?: string;
  fareRange?: string;
  seasonTips?: string;
  rawText: string;
}

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
  durationLabel: string;
  estimatedBudget?: string;
  overviewSummary: string;
  flights: ParsedFlightInfo;
  hotels: ParsedHotelItem[];
  itineraryDays: ParsedItineraryDay[];
  weather: ParsedWeatherInfo;
  recommendations: string[];
}
