import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchApi, type Opportunity, type TrendSummary } from "./api";

// ── Opportunities ──

export function useOpportunities(status?: string) {
  return useQuery({
    queryKey: ["opportunities", status],
    queryFn: () => {
      const params = status ? `?status=${status}` : "";
      return fetchApi<Opportunity[]>(`/opportunities/${params}`);
    },
  });
}

// ── Trends ──

export function useTrendSummary() {
  return useQuery({
    queryKey: ["trends", "summary"],
    queryFn: () => fetchApi<TrendSummary>("/trends/summary"),
    staleTime: 60 * 1000, // 60s for summary
  });
}

export function useScrapeAndScore() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await fetchApi("/trends/scrape", { method: "POST" });
      await fetchApi("/scoring/run", { method: "POST" });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["opportunities"] });
      queryClient.invalidateQueries({ queryKey: ["trends"] });
    },
  });
}

// ── Health ──

interface HealthDetailed {
  status: string;
  service: string;
  version: string;
  env: string;
  checks: Record<string, { status: string; latency_ms: number | null; error: string | null }>;
}

export function useHealthDetailed() {
  return useQuery({
    queryKey: ["health", "detailed"],
    queryFn: () => fetchApi<HealthDetailed>("/health/detailed"),
    staleTime: 15 * 1000,
    refetchInterval: 30 * 1000, // auto-poll every 30s
  });
}

// ── Printers ──

export interface PrinterData {
  id: string;
  model: string;
  serial: string;
  ip: string;
  status: string;
  last_seen: string | null;
  connection_type: string;
  location_label: string | null;
  capabilities_json: Record<string, unknown> | null;
}

export function usePrinters() {
  return useQuery({
    queryKey: ["printers"],
    queryFn: () => fetchApi<PrinterData[]>("/printers/"),
  });
}

export function useCreatePrinter() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<PrinterData>) =>
      fetchApi<PrinterData>("/printers/", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["printers"] });
    },
  });
}

export function useDeletePrinter() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      fetchApi(`/printers/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["printers"] });
    },
  });
}
