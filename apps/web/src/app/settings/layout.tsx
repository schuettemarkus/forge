"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Settings, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

const tabs = [
  { href: "/settings", label: "General", icon: Settings, exact: true },
  { href: "/settings/systems", label: "Systems", icon: Activity },
];

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="max-w-4xl">
      {/* Header */}
      <div className="mb-6 flex items-center gap-3">
        <div className="rounded-xl bg-gradient-to-br from-primary/30 to-accent/30 p-2.5">
          <Settings className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-sm text-muted-foreground">
            Manage store connections, printers, and system health
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-xl glass-strong p-1">
        {tabs.map((tab) => {
          const isActive = tab.exact
            ? pathname === tab.href
            : pathname.startsWith(tab.href);
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-primary/15 text-white shadow-sm"
                  : "text-muted-foreground hover:text-foreground hover:bg-white/5"
              )}
            >
              <tab.icon className={cn("h-4 w-4", isActive && "text-primary")} />
              {tab.label}
            </Link>
          );
        })}
      </div>

      {children}
    </div>
  );
}
