"use client";

import { Settings, Store, Printer, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const PLATFORMS = [
  { id: "etsy", name: "Etsy", description: "Handmade marketplace", connected: false },
  { id: "shopify", name: "Shopify", description: "Own your storefront", connected: false },
  { id: "woocommerce", name: "WooCommerce", description: "WordPress commerce", connected: false },
  { id: "manual", name: "Manual", description: "Enter orders manually", connected: true },
];

export default function SettingsPage() {
  return (
    <div className="max-w-3xl">
      <div className="mb-8 flex items-center gap-3">
        <div className="rounded-xl bg-gradient-to-br from-primary/30 to-accent/30 p-2.5">
          <Settings className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-sm text-muted-foreground">
            Manage store connections, printers, and preferences
          </p>
        </div>
      </div>

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
          <Button variant="outline" size="sm" className="rounded-xl">
            + Add Printer
          </Button>
        </div>
        <div className="glass rounded-2xl p-8 text-center">
          <Printer className="mx-auto mb-3 h-8 w-8 text-muted-foreground/40" />
          <p className="text-sm text-muted-foreground">No printers configured</p>
          <p className="text-xs text-muted-foreground/60 mt-1">
            Add your Bambu P1S or invite a friend&apos;s printer
          </p>
        </div>
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
    </div>
  );
}
