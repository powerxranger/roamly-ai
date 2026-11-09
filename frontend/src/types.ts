export interface TravelRequest {
  message: string;
  thread_id?: string | null;
}

export interface TravelSuccessResponse {
  success: true;
  thread_id: string;
  answer: string;
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

export type ConciergeTaskStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export interface ConciergeTask {
  id: string;
  label: string;
  sublabel: string;
  icon: 'flight' | 'hotel' | 'weather' | 'itinerary' | 'synthesis';
  status: ConciergeTaskStatus;
  technicalRole: string; // available for the tech specs modal
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
