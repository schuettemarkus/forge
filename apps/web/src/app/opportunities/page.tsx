import { Lightbulb } from "lucide-react";

export default function OpportunitiesPage() {
  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Lightbulb className="h-6 w-6 text-primary" />
        <h1 className="text-2xl font-bold">Opportunity Queue</h1>
        <span className="rounded-full bg-muted px-2.5 py-0.5 text-xs font-medium text-muted-foreground">
          0
        </span>
      </div>

      <div className="rounded-lg border border-border bg-card p-12 text-center">
        <Lightbulb className="mx-auto mb-4 h-12 w-12 text-muted-foreground/50" />
        <p className="text-lg font-medium text-muted-foreground">
          No opportunities yet
        </p>
        <p className="mt-1 text-sm text-muted-foreground/70">
          Trend scrapers will populate this queue once configured in M1.
        </p>
      </div>

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
