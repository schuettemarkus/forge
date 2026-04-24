import { DollarSign } from "lucide-react";

export default function FinancePage() {
  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <DollarSign className="h-6 w-6 text-primary" />
        <h1 className="text-2xl font-bold">Finance & P&L</h1>
      </div>

      <div className="rounded-lg border border-border bg-card p-12 text-center">
        <DollarSign className="mx-auto mb-4 h-12 w-12 text-muted-foreground/50" />
        <p className="text-lg font-medium text-muted-foreground">
          No financial data yet
        </p>
        <p className="mt-1 text-sm text-muted-foreground/70">
          Revenue, costs, and per-SKU P&L will populate once orders start flowing in M5.
        </p>
      </div>
    </div>
  );
}
