const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchApi<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

// Types matching the API response models
export interface Opportunity {
  id: string;
  concept: string;
  score: number;
  demand: number;
  competition: number;
  printability: number;
  margin_est: number;
  rationale_md: string | null;
  ip_status: string;
  status: string;
  created_at: string;
}

export interface TrendSignal {
  id: string;
  source: string;
  query: string;
  velocity: number;
  volume: number;
  geography: string | null;
  captured_at: string;
}

export interface TrendSummary {
  total_signals: number;
  by_source: Record<string, number>;
  latest_capture: string | null;
}
