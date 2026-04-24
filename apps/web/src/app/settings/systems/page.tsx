"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Database,
  HardDrive,
  Server,
  Wifi,
  WifiOff,
  RefreshCw,
  CheckCircle,
  Clock,
} from "lucide-react";
import { fetchApi } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface ServiceCheck {
  status: string;
  latency_ms: number | null;
  error: string | null;
}

interface HealthData {
  status: string;
  service: string;
  version: string;
  env: string;
  checks: Record<string, ServiceCheck>;
}

interface TrendSummary {
  total_signals: number;
  by_source: Record<string, number>;
  latest_capture: string | null;
}

const SERVICE_ICONS: Record<string, typeof Database> = {
  postgres: Database,
  redis: HardDrive,
  storage: Server,
};

const SERVICE_LABELS: Record<string, string> = {
  postgres: "PostgreSQL",
  redis: "Redis",
  storage: "Object Storage",
};

export default function SystemsPage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [trends, setTrends] = useState<TrendSummary | null>(null);
  const [apiUp, setApiUp] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      // Check basic API
      await fetchApi<Record<string, string>>("/health");
      setApiUp(true);

      // Detailed health
      try {
        const h = await fetchApi<HealthData>("/health/detailed");
        setHealth(h);
      } catch {
        setHealth(null);
      }

      // Trend summary
      try {
        const t = await fetchApi<TrendSummary>("/trends/summary");
        setTrends(t);
      } catch {
        setTrends(null);
      }
    } catch {
      setApiUp(false);
      setHealth(null);
      setTrends(null);
    } finally {
      setLoading(false);
      setLastChecked(new Date());
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 30000); // Auto-refresh every 30s
    return () => clearInterval(interval);
  }, [refresh]);

  const overallStatus = apiUp === false
    ? "offline"
    : health?.status === "ok"
    ? "healthy"
    : health?.status === "degraded"
    ? "degraded"
    : "unknown";

  return (
    <>
      {/* Toolbar */}
      <div className="mb-6 flex items-center justify-end gap-3">
        {lastChecked && (
          <span className="text-[11px] text-muted-foreground/50 flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {lastChecked.toLocaleTimeString()}
          </span>
        )}
        <Button onClick={refresh} disabled={loading} variant="outline" size="sm" className="rounded-xl">
          <RefreshCw className={`mr-2 h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Overall Status Banner */}
      <div className={`glass rounded-2xl p-4 sm:p-5 mb-4 sm:mb-6 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 ${
        overallStatus === "healthy" ? "glow-amber" : ""
      }`}>
        {overallStatus === "healthy" ? (
          <CheckCircle className="h-8 w-8 text-success" />
        ) : overallStatus === "offline" ? (
          <WifiOff className="h-8 w-8 text-destructive" />
        ) : (
          <Wifi className="h-8 w-8 text-warning" />
        )}
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold capitalize">{overallStatus}</h2>
            <Badge variant={
              overallStatus === "healthy" ? "success" :
              overallStatus === "degraded" ? "warning" : "destructive"
            }>
              {health?.env || "unknown"}
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            {overallStatus === "healthy"
              ? "All systems operational"
              : overallStatus === "offline"
              ? "API is unreachable — is the backend running?"
              : "Some services are experiencing issues"}
          </p>
        </div>
        {health && (
          <div className="sm:ml-auto sm:text-right">
            <span className="text-xs text-muted-foreground">Version</span>
            <p className="text-sm font-mono">{health.version}</p>
          </div>
        )}
      </div>

      {/* Service Cards */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider">Services</h3>
        <div className="grid gap-3">
          {/* API service */}
          <div className="glass rounded-2xl p-4 flex items-center gap-4">
            <div className={`rounded-xl p-2.5 ${apiUp ? "bg-success/10" : "bg-destructive/10"}`}>
              <Server className={`h-5 w-5 ${apiUp ? "text-success" : "text-destructive"}`} />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-medium">Forge API</span>
                <Badge variant={apiUp ? "success" : "destructive"}>
                  {apiUp ? "Online" : "Offline"}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">FastAPI application server</p>
            </div>
            <span className="text-xs text-muted-foreground font-mono">:8000</span>
          </div>

          {/* Downstream services */}
          {health?.checks && Object.entries(health.checks).map(([name, check]) => {
            const Icon = SERVICE_ICONS[name] || Server;
            const label = SERVICE_LABELS[name] || name;
            const isOk = check.status === "ok";

            return (
              <div key={name} className="glass rounded-2xl p-4 flex items-center gap-4">
                <div className={`rounded-xl p-2.5 ${isOk ? "bg-success/10" : "bg-destructive/10"}`}>
                  <Icon className={`h-5 w-5 ${isOk ? "text-success" : "text-destructive"}`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{label}</span>
                    <Badge variant={isOk ? "success" : "destructive"}>
                      {isOk ? "Online" : "Error"}
                    </Badge>
                  </div>
                  {check.error && (
                    <p className="text-xs text-destructive mt-0.5 truncate max-w-md">{check.error}</p>
                  )}
                </div>
                {check.latency_ms !== null && (
                  <span className="text-xs text-muted-foreground font-mono">
                    {check.latency_ms.toFixed(0)}ms
                  </span>
                )}
              </div>
            );
          })}

          {!health && apiUp && (
            <div className="glass rounded-2xl p-8 text-center">
              <RefreshCw className="mx-auto mb-3 h-6 w-6 animate-spin text-muted-foreground/30" />
              <p className="text-sm text-muted-foreground">Loading service details...</p>
            </div>
          )}
        </div>
      </div>

      {/* Data Pipeline Status */}
      <div>
        <h3 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider">Data Pipeline</h3>
        <div className="glass rounded-2xl p-5">
          {trends ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-2xl font-bold">{trends.total_signals.toLocaleString()}</span>
                  <span className="text-sm text-muted-foreground ml-2">total trend signals</span>
                </div>
                {trends.latest_capture && (
                  <div className="text-right">
                    <span className="text-xs text-muted-foreground">Last capture</span>
                    <p className="text-sm font-mono">
                      {new Date(trends.latest_capture).toLocaleString()}
                    </p>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {Object.entries(trends.by_source).map(([source, count]) => (
                  <div key={source} className="rounded-xl bg-white/5 p-3">
                    <span className="text-[10px] uppercase tracking-wider text-muted-foreground/60 block mb-1">
                      {source.replace("_", " ")}
                    </span>
                    <span className="text-lg font-bold">{count}</span>
                    <span className="text-xs text-muted-foreground ml-1">signals</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-sm text-muted-foreground">
                {apiUp ? "No trend data yet — run a scrape first" : "Connect to API to see pipeline status"}
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
