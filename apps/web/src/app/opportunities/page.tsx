"use client";

import { useEffect, useState, useCallback } from "react";
import { Lightbulb, TrendingUp, Shield, Printer, DollarSign, RefreshCw } from "lucide-react";
import { fetchApi, type Opportunity } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [selected, setSelected] = useState(0);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOpportunities = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchApi<Opportunity[]>("/opportunities/");
      setOpportunities(data);
      setError(null);
    } catch (e) {
      setError("API unavailable — start the backend with: make api");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOpportunities();
  }, [fetchOpportunities]);

  // Keyboard navigation
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "j" || e.key === "ArrowDown") {
        setSelected((s) => Math.min(s + 1, opportunities.length - 1));
      } else if (e.key === "k" || e.key === "ArrowUp") {
        setSelected((s) => Math.max(s - 1, 0));
      }
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [opportunities.length]);

  const triggerScrape = async () => {
    setScraping(true);
    try {
      await fetchApi("/trends/scrape", { method: "POST" });
      await fetchApi("/scoring/run", { method: "POST" });
      await fetchOpportunities();
    } catch (e) {
      setError("Scrape failed — is the backend running?");
    } finally {
      setScraping(false);
    }
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Lightbulb className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold">Opportunity Queue</h1>
          <Badge>{opportunities.length}</Badge>
        </div>
        <Button
          onClick={triggerScrape}
          disabled={scraping}
          variant="outline"
          size="sm"
        >
          <RefreshCw className={`mr-2 h-3 w-3 ${scraping ? "animate-spin" : ""}`} />
          {scraping ? "Scraping..." : "Scrape & Score"}
        </Button>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-warning/30 bg-warning/10 p-3 text-sm text-warning">
          {error}
        </div>
      )}

      {loading ? (
        <div className="rounded-lg border border-border bg-card p-12 text-center">
          <RefreshCw className="mx-auto mb-4 h-8 w-8 animate-spin text-muted-foreground/50" />
          <p className="text-muted-foreground">Loading opportunities...</p>
        </div>
      ) : opportunities.length === 0 ? (
        <div className="rounded-lg border border-border bg-card p-12 text-center">
          <Lightbulb className="mx-auto mb-4 h-12 w-12 text-muted-foreground/50" />
          <p className="text-lg font-medium text-muted-foreground">
            No opportunities yet
          </p>
          <p className="mt-1 text-sm text-muted-foreground/70">
            Click &quot;Scrape & Score&quot; to run the trend pipeline, or wait for the daily cron.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {opportunities.map((opp, i) => (
            <div
              key={opp.id}
              className={`rounded-lg border p-4 transition-colors cursor-pointer ${
                i === selected
                  ? "border-primary/50 bg-primary/5"
                  : "border-border bg-card hover:border-border/80"
              }`}
              onClick={() => setSelected(i)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold capitalize">{opp.concept}</h3>
                    <Badge
                      variant={
                        opp.score > 50 ? "success" : opp.score > 20 ? "warning" : "default"
                      }
                    >
                      {opp.score.toFixed(1)}
                    </Badge>
                    <Badge variant={opp.ip_status === "clear" ? "success" : "destructive"}>
                      {opp.ip_status}
                    </Badge>
                  </div>

                  <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <TrendingUp className="h-3 w-3" />
                      Demand: {opp.demand.toFixed(1)}
                    </span>
                    <span className="flex items-center gap-1">
                      <Shield className="h-3 w-3" />
                      Competition: {opp.competition.toFixed(1)}
                    </span>
                    <span className="flex items-center gap-1">
                      <Printer className="h-3 w-3" />
                      Printability: {(opp.printability * 100).toFixed(0)}%
                    </span>
                    <span className="flex items-center gap-1">
                      <DollarSign className="h-3 w-3" />
                      Margin: {opp.margin_est.toFixed(0)}%
                    </span>
                  </div>
                </div>

                <div className="flex gap-1">
                  <Button size="sm" variant="default">
                    Design
                  </Button>
                  <Button size="sm" variant="ghost">
                    Skip
                  </Button>
                </div>
              </div>

              {i === selected && opp.rationale_md && (
                <div className="mt-3 border-t border-border pt-3 text-sm text-muted-foreground whitespace-pre-line">
                  {opp.rationale_md}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 flex gap-4 text-xs text-muted-foreground/50">
        <span>
          <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono">J</kbd>
          <kbd className="ml-0.5 rounded bg-muted px-1.5 py-0.5 font-mono">K</kbd>
          {" "}Navigate
        </span>
        <span>
          <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono">A</kbd>
          {" "}Approve
        </span>
        <span>
          <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono">S</kbd>
          {" "}Skip
        </span>
        <span>
          <kbd className="rounded bg-muted px-1.5 py-0.5 font-mono">X</kbd>
          {" "}Blacklist
        </span>
      </div>
    </div>
  );
}
