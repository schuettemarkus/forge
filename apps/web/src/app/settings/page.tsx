"use client";

import Link from "next/link";
import { Store, Printer, Shield, ExternalLink } from "lucide-react";
import { usePrinters } from "@/lib/hooks";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const PLATFORMS = [
  { id: "etsy", name: "Etsy", description: "Handmade marketplace", connected: false },
  { id: "shopify", name: "Shopify", description: "Own your storefront", connected: false },
  { id: "woocommerce", name: "WooCommerce", description: "WordPress commerce", connected: false },
  { id: "manual", name: "Manual", description: "Enter orders manually", connected: true },
];

export default function SettingsPage() {
  const { data: printers = [] } = usePrinters();

  return (
    <>
      {/* Connected Stores */}
      <section className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Store className="h-4 w-4 text-primary" />
          <h2 className="text-lg font-semibold">Connected Stores</h2>
        </div>
        <div className="grid gap-3">
          {PLATFORMS.map((platform) => (
            <div key={platform.id} className="glass rounded-2xl p-4 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{platform.name}</span>
                  {platform.connected ? (
                    <Badge variant="success">Connected</Badge>
                  ) : (
                    <Badge>Not connected</Badge>
                  )}
                </div>
                <p className="text-xs text-muted-foreground mt-0.5">{platform.description}</p>
              </div>
              <Button
                variant={platform.connected ? "ghost" : "outline"}
                size="sm"
                className="rounded-xl"
              >
                {platform.connected ? "Configure" : "Connect"}
              </Button>
            </div>
          ))}
        </div>
      </section>

      {/* Printers */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Printer className="h-4 w-4 text-accent" />
            <h2 className="text-lg font-semibold">Printers</h2>
          </div>
          <Link href="/farm?add=1">
            <Button variant="outline" size="sm" className="rounded-xl">
              + Add Printer
            </Button>
          </Link>
        </div>

        {printers.length === 0 ? (
          <Link href="/farm?add=1" className="block">
            <div className="glass rounded-2xl p-8 text-center border border-dashed border-white/10 hover:border-primary/30 hover:bg-primary/5 transition-all duration-200 group cursor-pointer">
              <Printer className="mx-auto mb-3 h-8 w-8 text-muted-foreground/40 group-hover:text-primary/50 transition-colors" />
              <p className="text-sm text-muted-foreground group-hover:text-foreground/80 transition-colors">
                No printers configured
              </p>
              <p className="text-xs text-muted-foreground/60 mt-1">
                Click to add your first printer
              </p>
            </div>
          </Link>
        ) : (
          <div className="space-y-2">
            {printers.map((printer) => (
              <div key={printer.id} className="glass rounded-2xl p-4 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{printer.model}</span>
                    <Badge variant={printer.status === "online" || printer.status === "idle" ? "success" : "default"}>
                      {printer.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5 font-mono">{printer.ip}</p>
                </div>
                <Link href="/farm">
                  <Button variant="ghost" size="sm" className="rounded-xl text-muted-foreground">
                    <ExternalLink className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </div>
            ))}
            <Link href="/farm?add=1" className="block">
              <div className="rounded-2xl border border-dashed border-white/10 hover:border-primary/30 hover:bg-primary/5 py-2.5 flex items-center justify-center gap-2 text-xs text-muted-foreground/50 hover:text-muted-foreground transition-all duration-200">
                + Add another printer
              </div>
            </Link>
          </div>
        )}
      </section>

      {/* Security */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <Shield className="h-4 w-4 text-secondary" />
          <h2 className="text-lg font-semibold">Security</h2>
        </div>
        <div className="glass rounded-2xl p-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium">API Keys</span>
              <p className="text-xs text-muted-foreground mt-0.5">
                Store credentials are encrypted at rest
              </p>
            </div>
            <Badge variant="success">Encrypted</Badge>
          </div>
        </div>
      </section>
    </>
  );
}
