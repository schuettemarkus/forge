import { Cuboid } from "lucide-react";

export default function DesignsPage() {
  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Cuboid className="h-6 w-6 text-primary" />
        <h1 className="text-2xl font-bold">Design Review</h1>
      </div>

      <div className="rounded-lg border border-border bg-card p-12 text-center">
        <Cuboid className="mx-auto mb-4 h-12 w-12 text-muted-foreground/50" />
        <p className="text-lg font-medium text-muted-foreground">
          No designs pending review
        </p>
        <p className="mt-1 text-sm text-muted-foreground/70">
          Approve opportunities first, then designs will appear here for QA review.
        </p>
      </div>
    </div>
  );
}
