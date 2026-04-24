"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Lightbulb,
  Cuboid,
  Cpu,
  Package,
  DollarSign,
  Settings,
  Menu,
  X,
  LogOut,
  User,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";

const navItems = [
  { href: "/opportunities", label: "Opportunities", icon: Lightbulb },
  { href: "/designs", label: "Designs", icon: Cuboid },
  { href: "/farm", label: "Farm", icon: Cpu },
  { href: "/orders", label: "Orders", icon: Package },
  { href: "/finance", label: "Finance", icon: DollarSign },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isAuthenticated, email, logout } = useAuth();
  const [open, setOpen] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setOpen(false);
  }, [pathname]);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  return (
    <>
      {/* Mobile top bar */}
      <div className="fixed top-0 left-0 right-0 z-50 flex h-14 items-center justify-between px-4 glass-strong lg:hidden">
        <div className="flex items-center gap-2">
          <img src="/logo.svg" alt="Forge" className="h-6 w-6" />
          <span className="text-lg font-bold tracking-wider text-gradient">FORGE</span>
        </div>
        <button
          onClick={() => setOpen(!open)}
          className="rounded-lg p-2 text-muted-foreground hover:text-foreground hover:bg-white/10 transition-colors"
          aria-label="Toggle menu"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Backdrop overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={cn(
          "fixed top-0 left-0 z-50 flex h-screen w-64 flex-col glass-strong transition-transform duration-300 ease-out",
          "lg:w-56 lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex h-16 items-center gap-2.5 px-5">
          <img src="/logo.svg" alt="Forge" className="h-7 w-7" />
          <span className="text-xl font-bold tracking-wider text-gradient">FORGE</span>
          <span className="ml-auto rounded-full bg-primary/20 px-2 py-0.5 text-[10px] font-semibold text-primary">
            v0.1
          </span>
        </div>

        <nav className="flex-1 space-y-0.5 px-3 pt-2 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-3 lg:py-2.5 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "glass bg-primary/15 text-white shadow-sm"
                    : "text-muted-foreground hover:text-foreground hover:bg-white/5"
                )}
              >
                <item.icon className={cn("h-5 w-5 lg:h-4 lg:w-4", isActive && "text-primary")} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-border p-3 space-y-1">
          <Link
            href="/settings"
            className={cn(
              "flex items-center gap-3 rounded-xl px-3 py-3 lg:py-2.5 text-sm transition-all",
              pathname.startsWith("/settings")
                ? "glass bg-primary/15 text-white shadow-sm"
                : "text-muted-foreground hover:text-foreground hover:bg-white/5"
            )}
          >
            <Settings className={cn("h-5 w-5 lg:h-4 lg:w-4", pathname.startsWith("/settings") && "text-primary")} />
            Settings
          </Link>

          {isAuthenticated ? (
            <div className="flex items-center justify-between px-3 py-2">
              <div className="flex items-center gap-2 min-w-0">
                <User className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                <span className="text-[11px] text-muted-foreground truncate">
                  {email}
                </span>
              </div>
              <button
                onClick={logout}
                className="text-muted-foreground/50 hover:text-destructive transition-colors shrink-0 ml-1"
                title="Sign out"
              >
                <LogOut className="h-3.5 w-3.5" />
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-muted-foreground hover:text-foreground hover:bg-white/5 transition-all"
            >
              <User className="h-4 w-4" />
              Sign In
            </Link>
          )}

          <div className="flex items-center gap-2 px-3 py-1">
            <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
            <span className="text-[11px] text-muted-foreground">System Online</span>
          </div>
        </div>
      </aside>
    </>
  );
}
