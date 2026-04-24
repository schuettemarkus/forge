"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Lightbulb,
  TrendingUp,
  Shield,
  Printer,
  DollarSign,
  RefreshCw,
  Sparkles,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { fetchApi, type Opportunity } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScoreRing } from "@/components/score-ring";

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [selected, setSelected] = useState(0);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchOpportunities = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchApi<Opportunity[]>("/opportunities/");
      setOpportunities(data);
      setError(null);
    } catch {
      setError("API unavailable — start the backend with: make api");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOpportunities();
  }, [fetchOpportunities]);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "j" || e.key === "ArrowDown") {
        setSelected((s) => Math.min(s + 1, opportunities.length - 1));
      } else if (e.key === "k" || e.key === "ArrowUp") {
        setSelected((s) => Math.max(s - 1, 0));
      } else if (e.key === "Enter") {
        const opp = opportunities[selected];
        if (opp) setExpanded(expanded === opp.id ? null : opp.id);
      }
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [opportunities.length, selected, expanded, opportunities]);

  const triggerScrape = async () => {
    setScraping(true);
    try {
      await fetchApi("/trends/scrape", { method: "POST" });
      await fetchApi("/scoring/run", { method: "POST" });
      await fetchOpportunities();
    } catch {
      setError("Scrape failed — is the backend running?");
    } finally {
      setScraping(false);
    }
  };

  const getPrintabilityLabel = (p: number) => {
    if (p >= 0.8) return "Easy";
    if (p >= 0.5) return "Moderate";
    return "Complex";
  };

  return (
    <div className="max-w-4xl">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-gradient-to-br from-primary/30 to-secondary/30 p-2.5">
              <Lightbulb className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Opportunities</h1>
              <p className="text-sm text-muted-foreground">
                {opportunities.length} product ideas ranked by potential
              </p>
            </div>
          </div>
        </div>
        <Button
          onClick={triggerScrape}
          disabled={scraping}
          size="sm"
          className="rounded-xl"
        >
          <RefreshCw className={`mr-2 h-3.5 w-3.5 ${scraping ? "animate-spin" : ""}`} />
          {scraping ? "Scanning..." : "Scan Trends"}
        </Button>
      </div>

      {error && (
        <div className="mb-4 glass rounded-xl p-3 text-sm text-warning border border-warning/20">
          {error}
        </div>
      )}

      {loading ? (
        <div className="glass rounded-2xl p-16 text-center">
          <RefreshCw className="mx-auto mb-4 h-8 w-8 animate-spin text-primary/50" />
          <p className="text-muted-foreground">Loading opportunities...</p>
        </div>
      ) : opportunities.length === 0 ? (
        <div className="glass rounded-2xl p-16 text-center">
          <div className="mx-auto mb-4 w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
            <Sparkles className="h-8 w-8 text-primary/60" />
          </div>
          <p className="text-lg font-medium text-foreground/80">
            No opportunities yet
          </p>
          <p className="mt-2 text-sm text-muted-foreground max-w-md mx-auto">
            Hit &quot;Scan Trends&quot; to pull trending data from Google Trends, Reddit, Etsy, and maker communities.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {opportunities.map((opp, i) => {
            const isSelected = i === selected;
            const isExpanded = expanded === opp.id;

            return (
              <div
                key={opp.id}
                className={`glass rounded-2xl p-5 transition-all duration-200 cursor-pointer ${
                  isSelected ? "ring-1 ring-primary/40 glow-pink" : "hover:bg-white/5"
                }`}
                onClick={() => {
                  setSelected(i);
                  setExpanded(isExpanded ? null : opp.id);
                }}
              >
                <div className="flex items-center gap-4">
                  {/* Score ring */}
                  <ScoreRing score={opp.score} max={10} size={52} />

                  {/* Main content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold capitalize truncate">
                        {opp.concept}
                      </h3>
                      <Badge
                        variant={opp.ip_status === "clear" ? "success" : "destructive"}
                      >
                        {opp.ip_status === "clear" ? "IP Clear" : "IP Flag"}
                      </Badge>
                    </div>

                    {/* Metric pills */}
                    <div className="flex flex-wrap gap-2">
                      <span className="inline-flex items-center gap-1 rounded-lg bg-white/5 px-2.5 py-1 text-xs text-muted-foreground">
                        <TrendingUp className="h-3 w-3 text-primary" />
                        {opp.demand.toFixed(0)} demand
                      </span>
                      <span className="inline-flex items-center gap-1 rounded-lg bg-white/5 px-2.5 py-1 text-xs text-muted-foreground">
                        <Shield className="h-3 w-3 text-secondary" />
                        {opp.competition.toFixed(1)} competition
                      </span>
                      <span className="inline-flex items-center gap-1 rounded-lg bg-white/5 px-2.5 py-1 text-xs text-muted-foreground">
                        <Printer className="h-3 w-3 text-accent" />
                        {getPrintabilityLabel(opp.printability)}
                      </span>
                      <span className="inline-flex items-center gap-1 rounded-lg bg-white/5 px-2.5 py-1 text-xs text-muted-foreground">
                        <DollarSign className="h-3 w-3 text-success" />
                        {opp.margin_est.toFixed(0)}% margin
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <Button size="sm" className="rounded-xl bg-gradient-to-r from-primary to-secondary hover:opacity-90">
                      <Sparkles className="mr-1.5 h-3 w-3" />
                      Design
                    </Button>
                    <button className="p-1 text-muted-foreground hover:text-foreground transition-colors">
                      {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {/* Expanded details */}
                {isExpanded && opp.rationale_md && (
                  <div className="mt-4 pt-4 border-t border-white/5">
                    <RationaleView rationale={opp.rationale_md} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Keyboard hints */}
      <div className="mt-6 flex gap-4 text-[11px] text-muted-foreground/40">
        <span>
          <kbd className="rounded bg-white/5 px-1.5 py-0.5 font-mono text-[10px]">J</kbd>
          <kbd className="ml-0.5 rounded bg-white/5 px-1.5 py-0.5 font-mono text-[10px]">K</kbd>
          {" "}Navigate
        </span>
        <span>
          <kbd className="rounded bg-white/5 px-1.5 py-0.5 font-mono text-[10px]">Enter</kbd>
          {" "}Expand
        </span>
        <span>
          <kbd className="rounded bg-white/5 px-1.5 py-0.5 font-mono text-[10px]">A</kbd>
          {" "}Design
        </span>
      </div>
    </div>
  );
}

/** Parse the markdown rationale into a clean visual display */
function RationaleView({ rationale }: { rationale: string }) {
  const lines = rationale.split("\n").filter((l) => l.trim());
  const recommendation = lines.find((l) => l.startsWith("**Recommendation:**"));
  const recText = recommendation?.replace("**Recommendation:** ", "") || "";

  return (
    <div className="space-y-3">
      {/* Recommendation callout */}
      {recText && (
        <div className="rounded-xl bg-gradient-to-r from-primary/10 to-secondary/10 p-3 text-sm">
          <span className="font-medium text-foreground/90">{recText}</span>
        </div>
      )}

      {/* Signal details */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        {lines
          .filter((l) => l.startsWith("**") && !l.startsWith("##") && !l.startsWith("**Recommendation"))
          .map((line, idx) => {
            const match = line.match(/\*\*(.+?):\*\*\s*(.+)/);
            if (!match) return null;
            return (
              <div key={idx} className="rounded-lg bg-white/5 p-2.5">
                <span className="block text-muted-foreground/60 text-[10px] uppercase tracking-wider mb-0.5">
                  {match[1]}
                </span>
                <span className="text-foreground/80">{match[2]}</span>
              </div>
            );
          })}
      </div>
    </div>
  );
}
