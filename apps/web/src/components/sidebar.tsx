"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Lightbulb,
  Cuboid,
  Cpu,
  Package,
  DollarSign,
  Activity,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/opportunities", label: "Opportunities", icon: Lightbulb },
  { href: "/designs", label: "Designs", icon: Cuboid },
  { href: "/farm", label: "Farm", icon: Cpu },
  { href: "/orders", label: "Orders", icon: Package },
  { href: "/finance", label: "Finance", icon: DollarSign },
  { href: "/systems", label: "Systems", icon: Activity },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-56 flex-col glass-strong">
      <div className="flex h-16 items-center gap-2.5 px-5">
        <img src="/logo.svg" alt="Forge" className="h-7 w-7" />
        <span className="text-xl font-bold tracking-wider text-gradient">
          FORGE
        </span>
        <span className="ml-auto rounded-full bg-primary/20 px-2 py-0.5 text-[10px] font-semibold text-primary">
          v0.1
        </span>
      </div>

      <nav className="flex-1 space-y-0.5 px-3 pt-2">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
                isActive
                  ? "glass bg-primary/15 text-white shadow-sm"
                  : "text-muted-foreground hover:text-foreground hover:bg-white/5"
              )}
            >
              <item.icon className={cn("h-4 w-4", isActive && "text-primary")} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border p-3">
        <Link
          href="/settings"
          className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all"
        >
          <Settings className="h-4 w-4" />
          Settings
        </Link>
        <div className="flex items-center gap-2 px-3 py-2 mt-1">
          <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
          <span className="text-[11px] text-muted-foreground">System Online</span>
        </div>
      </div>
    </aside>
  );
}
