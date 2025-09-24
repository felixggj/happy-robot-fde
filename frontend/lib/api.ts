const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://backend-fde-production.up.railway.app";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY;

interface MetricsResponse {
  total_calls: number;
  conversion_rate: number;
  avg_negotiation_rounds: number;
  outcomes: Record<string, number>;
  sentiment: Record<string, number>;
  total_revenue: number;
}

interface LoadSearchResponse {
  load_id: string;
  origin: string;
  destination: string;
  pickup_datetime: string;
  delivery_datetime: string;
  equipment_type: string;
  loadboard_rate: number;
  notes?: string;
  weight?: number;
  commodity_type?: string;
  num_of_pieces?: number;
  miles?: number;
  dimensions?: string;
  score: number;
}

interface CallSessionResponse {
  session_id: string;
  carrier_mc: string;
  carrier_name: string;
  load_id: string;
  initial_rate: number;
  negotiated_rate: number | null;
  negotiation_rounds: number;
  outcome: string;
  sentiment: string;
  call_duration: number;
  created_at: string;
}

async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY || "",
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return response.json();
}

export async function getMetrics(): Promise<MetricsResponse> {
  return apiRequest("/api/metrics");
}

export async function getLoads(params?: {
  origin?: string;
  destination?: string;
  equipment_type?: string;
  max_results?: number;
}): Promise<LoadSearchResponse[]> {
  const searchParams = new URLSearchParams();
  if (params?.origin) searchParams.append("origin", params.origin);
  if (params?.destination)
    searchParams.append("destination", params.destination);
  if (params?.equipment_type)
    searchParams.append("equipment_type", params.equipment_type);
  if (params?.max_results)
    searchParams.append("max_results", params.max_results.toString());

  const queryString = searchParams.toString();
  return apiRequest(`/api/loads/search${queryString ? `?${queryString}` : ""}`);
}

export async function getCallSessions(
  limit?: number
): Promise<CallSessionResponse[]> {
  const params = limit ? `?limit=${limit}` : "";
  return apiRequest(`/api/call-sessions${params}`);
}

export async function getHealthStatus() {
  return apiRequest("/api/health");
}
