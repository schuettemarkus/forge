import { Package } from "lucide-react";

export default function OrdersPage() {
  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <Package className="h-6 w-6 text-primary" />
        <h1 className="text-2xl font-bold">Orders</h1>
      </div>

      <div className="rounded-lg border border-border bg-card p-12 text-center">
        <Package className="mx-auto mb-4 h-12 w-12 text-muted-foreground/50" />
        <p className="text-lg font-medium text-muted-foreground">
          No orders yet
        </p>
        <p className="mt-1 text-sm text-muted-foreground/70">
          Orders will flow in from Etsy and Shopify once listings go live in M3.
        </p>
      </div>
    </div>
  );
}
