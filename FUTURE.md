# Forge — Future Ideas (Out of Scope for v1)

Ideas that came up but don't belong in v1. Revisit after the system is profitable.

- **TikTok Shop integration** — high-volume potential but different fulfillment expectations
- **Amazon Handmade** — larger market but higher competition and fees
- **eBay integration** — low priority, different buyer demographics
- **Mobile app** — operator dashboard as PWA could work, native app is overkill
- **Customer-facing AI chat** — "describe what you want, we'll print it" — cool but complex
- **Multi-tenant SaaS** — let other print farm operators use Forge — major scope expansion
- **Auto-recovery from print failures** — beyond pause-and-alert, actually restart/retry
- **Robotic arm pick-and-place** — remove prints from bed automatically
- **AR preview for customers** — view the print in their space before buying
- **Subscription boxes** — monthly curated prints
- **Wholesale / B2B** — bulk orders for offices, schools
- **Print-on-demand API** — let other Etsy sellers use our farm

---

## v2 Sprint: User Profile, Settings & Data Persistence

**Priority: High — foundational for multi-session reliability**

### Profile, Login & Settings
- User profile with login/auth (upgrade from single-operator magic link to full account system)
- Settings panel: configure shop name, notification preferences, margin targets, scraper schedules
- Printer brand/model selector — support beyond Bambu (Prusa, Creality, Ankermake, Elegoo, etc.) with per-brand slicer profiles and build plate specs
- Printer profiles should be saveable presets (filament defaults, print speeds, quality tiers)

### Farm Page — Editable & Configurable Printers
- Add/edit/remove printers from the dashboard UI (not just config files)
- Per-printer settings: name, IP, model, AMS config, default filament, maintenance schedule
- Printer grouping and tagging (e.g. "PLA farm", "PETG specialty")

### Data Persistence & Consistency
- All application data persisted to Postgres — no ephemeral state
- Client-side caching (TanStack Query with stale-while-revalidate) so dashboard loads instantly
- Session continuity: users see the same numbers across tabs, devices, and sessions
- Deploy migrations must be non-destructive: additive schema changes only, no data loss on updates
- Seed data and user config stored separately from scraper/transactional data
- Backup/restore strategy for trend history, opportunities, and financial data
