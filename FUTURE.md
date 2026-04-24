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

---

## v3 Sprint: Universal Store Connector + Distributed Printer Network

**Priority: High — transforms Forge from single-operator to distributed print network**

### Universal Store Connector
- Connect to ANY online store via a plugin pattern (not just Etsy/Shopify)
- Store connector abstraction: base class with `sync_listing()`, `fetch_orders()`, `update_tracking()`
- Platform registry: Etsy, Shopify, WooCommerce, Squarespace, manual entry
- New `store_connection` table with encrypted credentials (replaces hardcoded API keys)
- `listing_store_link` junction table (replaces etsy_listing_id/shopify_product_id columns)
- Adding a new marketplace = one connector file + one line in the registry

### Distributed Printer Network
- Connect to printers you don't own — e.g., a friend's printer for fulfillment
- Remote printers connect via outbound WebSocket (no port forwarding needed)
- Pairing flow: invite code → API key exchange → bcrypt-hashed auth
- `operator` table for multi-user support (store owner vs printer operator roles)
- Printer capabilities matching: build volume, filament types, nozzle sizes

### Smart Job Routing
- Orders auto-route to available printers based on design requirements vs printer capabilities
- Priority: local > remote, fewest queued jobs wins
- Manual override via dashboard for any assignment
- Retry queue: unmatched jobs re-checked every 5 minutes

### Security
- Store API keys Fernet-encrypted at rest, never in API responses
- Remote printer API keys bcrypt-hashed, plaintext shown once during pairing
- WebSocket heartbeat with 30s timeout
- Rate-limited invite code generation
