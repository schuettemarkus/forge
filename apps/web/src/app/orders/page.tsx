import { Package } from "lucide-react";

export default function OrdersPage() {
  return (
    <div>
      <div className="mb-4 sm:mb-6 flex items-center gap-3">
        <Package className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
        <h1 className="text-xl sm:text-2xl font-bold">Orders</h1>
      </div>

      <div className="rounded-lg border border-border bg-card p-8 sm:p-12 text-center">
        <Package className="mx-auto mb-4 h-8 w-8 sm:h-12 sm:w-12 text-muted-foreground/50" />
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
