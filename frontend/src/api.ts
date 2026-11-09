import { HealthResponse, TravelRequest, TravelSuccessResponse } from './types';

// In production on Vercel, VITE_API_BASE_URL points to the Render backend URL (e.g., https://roamly-backend.onrender.com)
// In local dev, an empty string uses Vite's proxy configured in vite.config.ts
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');

export class ApiError extends Error {
  status: number;
  rawError?: string;
  missing?: string[];

  constructor(message: string, status: number, rawError?: string, missing?: string[]) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.rawError = rawError;
    this.missing = missing;
  }
}

export async function checkHealth(): Promise<HealthResponse> {
  const url = `${BASE_URL}/health`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new ApiError(`Health check failed with HTTP ${response.status}`, response.status);
  }
  return response.json();
}

export async function planTravel(request: TravelRequest): Promise<TravelSuccessResponse> {
  const url = `${BASE_URL}/api/travel`;

  let response: Response;
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : 'Network error';
    throw new ApiError(
      `Unable to connect to Roamly backend server. Please verify the backend is running. (${errorMsg})`,
      0
    );
  }

  let data: any;
  try {
    data = await response.json();
  } catch {
    throw new ApiError(
      `Received invalid response from server (HTTP ${response.status}).`,
      response.status
    );
  }

  if (!response.ok || !data.success) {
    const errorMessage = data?.error || `Request failed with HTTP ${response.status}`;
    throw new ApiError(errorMessage, response.status, data?.raw_error, data?.missing);
  }

  return data as TravelSuccessResponse;
}
