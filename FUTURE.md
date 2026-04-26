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

# Sprint Roadmap (Reprioritized 2026-04-24)

## Completed Sprints

- **M0: Skeleton** — monorepo, 15 DB tables, Docker/Makefile, FastAPI + Next.js
- **M1: Trend Intelligence** — 5 scrapers, opportunity scorer, 23 live opportunities
- **v2: Profiles & Persistence** — login, auth context, TanStack Query, printer CRUD, settings API
- **v3: Store Connectors (data model)** — plugin architecture, Etsy/Shopify/Manual connectors, store_connection table
- **v4: Security** — JWT auth, input validation, error handling, CORS, scraper fixes
- **v5: Performance** — parallel scrapers, 7 DB indexes, async storage, pool tuning
- **v6: QA System** — 19 tests, health probes, monitoring page, CI pipeline

---

## NEXT UP: v8 Sprint — Product Pipeline (Design → List → Sell)

**Priority: CRITICAL — this is the revenue path. Nothing else matters until this works.**

> Without this sprint, Forge is a research tool that finds trending products but
> can't make or sell them. This sprint closes the loop from "opportunity scored"
> to "money in the bank."

### Feature 1: Design Generation (Opportunity → Printable File)

The "Design" button on opportunities currently does nothing. After this sprint, clicking it generates a printable 3MF/STL file.

**What gets built:**
- `design_pipeline` service orchestrating the three generation paths:
  - **Parametric (preferred):** CadQuery/OpenSCAD templates for 5 starter categories: organizer, planter, hook, phone stand, cookie cutter. LLM fills parameters (size, style) from the opportunity concept.
  - **AI generation (fallback):** Meshy API integration for concepts that don't fit templates. Send concept description → receive mesh → validate.
- Printability gate on every generated file:
  - Mesh integrity check (manifold, no holes) via trimesh
  - Bounding box validation against P1S build plate (256x256x256mm)
  - Wall thickness check (≥1.2mm)
  - Slicer dry-run to extract: estimated print time, filament grams, cost
- QA report saved to `qa_report` table with pass/fail + cost breakdown
- Dashboard: "Design" button triggers generation → shows progress → displays result with render + cost + time estimate
- Status flow: opportunity `pending` → `designing` → design `ready` or `failed`

**API endpoints:**
- `POST /designs/generate/{opportunity_id}` — trigger design generation
- `GET /designs/{design_id}` — get design with QA report
- `GET /designs/?opportunity_id=X` — list designs for an opportunity

**Files:** `apps/api/app/services/design_pipeline.py`, `apps/api/app/services/parametric/`, `apps/api/app/routers/designs.py`

### Feature 2: Listing Creation (Design → Live on Etsy)

Once a design passes QA, generate marketplace-ready copy + images and publish.

**What gets built:**
- `listing_generator` service:
  - Claude API generates: title (SEO, ≤140 chars), description (features, dimensions, materials, care), 13 tags from trend signals
  - Pricing engine: cost estimate × (1 + margin_target) × competition adjustment, rounded to psychological price points ($X.99), never below cost + 40%
  - Product images: for v8, use the 3D render from design generation (turntable views). Lifestyle compositing is a future enhancement.
- Listing review screen in dashboard:
  - Preview card showing: title, description, tags, price, renders, cost breakdown
  - Edit any field before publishing
  - "Publish" button pushes to connected store via connector's `sync_listing()`
- Etsy connector `sync_listing()` actually implemented (currently a stub)
- Status flow: design `ready` → listing `draft` → operator reviews → `published`

**API endpoints:**
- `POST /listings/generate/{design_id}` — generate copy + price + images
- `PUT /listings/{listing_id}` — edit before publish
- `POST /listings/{listing_id}/publish` — push to connected store

**Files:** `apps/api/app/services/listing_generator.py`, `apps/api/app/services/pricing.py`, enhanced `apps/api/app/routers/listings.py`

### Feature 3: Order Fulfillment (Order → Print → Ship)

Once a listing is live, handle incoming orders end-to-end.

**What gets built:**
- Order webhook receiver:
  - `POST /webhooks/etsy` and `POST /webhooks/shopify` — receive order notifications
  - Validate, deduplicate (idempotent on external_id), persist to `order` table
  - Auto-create `print_job` linked to the order's SKU → design → gcode
- Job routing to printer:
  - Match order's design requirements to available printers
  - For v8 (single printer): assign to the one configured P1S
  - Update printer status, enqueue job
- Fulfillment flow:
  - Dashboard orders page shows real orders with status timeline
  - Mark as "printing" → "printed" → generate shipping label (Shippo API stub) → "shipped"
  - Enter tracking number → pushes to marketplace via connector's `update_tracking()`
- Ledger entries: every order creates cost/revenue records for P&L tracking

**API endpoints:**
- `POST /webhooks/{platform}` — order webhook (unauthenticated, signature-verified)
- `GET /orders/` — list with status filters (enhanced from current stub)
- `PUT /orders/{order_id}/status` — update fulfillment status
- `POST /orders/{order_id}/ship` — generate label + mark shipped

**Files:** `apps/api/app/routers/webhooks.py`, `apps/api/app/services/fulfillment.py`, enhanced `apps/api/app/routers/orders.py`

### Sprint Sequencing (3 weeks)

| Week | Deliverable | Acceptance Test |
|------|-------------|-----------------|
| 1 | Design generation + parametric templates + QA gate | Click "Design" on an opportunity → get a printable file with cost estimate in <90s |
| 2 | Listing generator + review screen + Etsy publish | Approve a design → see listing preview → publish to Etsy sandbox |
| 3 | Order webhooks + fulfillment flow + shipping | Test order from Etsy → appears in dashboard → mark shipped → tracking pushed back |

---

## Remaining Sprints (reprioritized)

### v3 Remaining: Distributed Printer Network
**Priority: After first sales — scale when you hit P1S capacity**

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

## ~~v3 Sprint: Universal Store Connector~~ DATA MODEL COMPLETED — remaining work below

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

---

## ~~v4 Sprint: Security Hardening~~ COMPLETED

### Authentication & Authorization
- Implement real JWT auth (replace stub magic-link/verify endpoints that currently return hardcoded tokens)
- Auth middleware on ALL API endpoints — currently every endpoint is fully unauthenticated
- Role-based access: operator vs printer_operator, scoped to owned resources
- Token refresh flow with short-lived access tokens (15min) + long-lived refresh tokens
- Rate limiting on auth endpoints (5 attempts/min)

### Input Validation & Injection Prevention
- Bound all query parameters: `limit` capped at 100, `offset` >= 0, `status`/`source` validated against enum
- Fix `opportunities/{id}` endpoint: uses `scalar_one()` which crashes on missing ID — switch to `scalar_one_or_none()` + proper 404
- Validate scraper POST endpoints with request body schemas
- Add request size limits (1MB default) to prevent payload DoS

### Secrets & Credential Management
- Encrypt `store_connection.credentials_json` with Fernet (currently stored as plaintext JSON despite comment saying "encrypted in prod")
- Enforce SECRET_KEY is not the default `"change-me-in-production"` — fail startup if unchanged
- Never return credentials in API responses — add response model filtering
- Rotate-friendly key management: support multiple active encryption keys for zero-downtime rotation

### API Security
- Tighten CORS: whitelist specific methods (GET, POST, PUT, DELETE) and headers instead of `["*"]`
- Add rate limiting middleware (slowapi or custom): 100 req/min general, 5/min on scrape endpoints
- Add request ID middleware for tracing + abuse detection
- HTTPS enforcement in production (redirect HTTP → HTTPS)

### Scraper Safety
- Fix Reddit scraper auth check: line 49 checks `ETSY_API_KEY` instead of Reddit credentials (copy-paste bug)
- Add per-scraper rate limit enforcement (not just sleep timers — track request counts)
- Sanitize scraped content before DB storage — validate types, cap string lengths
- Add SSRF protection: validate scraper target URLs against allowlist

### Data Protection
- IP blocklist bypass hardening: supplement substring matching with fuzzy matching / normalized comparison
- Add audit logging for all data mutations (who changed what, when)
- PII handling: hash customer data before storage, never log raw customer info
- Add SQL statement timeouts to prevent long-running queries from locking DB

### Code Hygiene
- Remove `sys.path.insert()` hack in scorer.py — use proper Python package imports
- Add security headers middleware (X-Content-Type-Options, X-Frame-Options, CSP)
- Dependency vulnerability scanning (pip-audit, npm audit) as pre-commit check

---

## ~~v5 Sprint: Performance & Speed~~ COMPLETED

### Database Optimization
- Add indexes on hot query paths: `(deleted_at, status)` on opportunity, `(source, captured_at)` on trend_signal, `concept` on opportunity
- Add pagination to `/opportunities/` endpoint (currently returns ALL rows unbounded)
- Combine trend summary endpoint's 3 separate queries into single aggregate query
- Add DB statement timeout (30s) to prevent runaway queries from blocking pool
- Deduplicate opportunities: add unique constraint on `(concept, DATE(created_at))` to prevent scorer from creating duplicates on repeated runs

### Async & Concurrency
- Parallelize scrapers with `asyncio.gather()` instead of sequential loop — 5x speedup on scrape runs
- Replace synchronous `boto3` in storage service with `aioboto3` or `run_in_executor()` — currently blocks the async event loop on every S3 upload
- Increase DB connection pool: `pool_size=20, max_overflow=30` (currently 5+10 which exhausts under concurrent scrapers + API requests)
- Add connection pool pre-ping to detect stale connections

### Frontend Performance
- Add TanStack Query (React Query) with stale-while-revalidate: 30s cache for opportunities, 60s for trends
- Deduplicate API calls (currently `fetchOpportunities()` called multiple times without dedup)
- Add `loading.tsx` Suspense boundaries for each route
- Virtualize opportunity list for large datasets (react-window or @tanstack/virtual)
- Next.js config: enable compression, image optimization, SWC minification

### Celery & Task Performance
- Add idempotency keys to prevent duplicate opportunity creation on task retry
- Add task timeouts (5min per scraper, 10min for full pipeline)
- Add concurrency controls: max 1 scrape_and_score task at a time (prevent overlapping runs)
- Configure result expiry (24h) to prevent Redis memory growth

### Caching Layer
- Add Redis caching for expensive endpoints: opportunity list (TTL 30s), trend summary (TTL 60s)
- Cache scraper results to avoid re-scraping within cooldown period (1hr per source)
- Add ETag/If-None-Match support for dashboard polling
- Implement cache invalidation on data mutations (new scrape, new score, status change)

### Monitoring & Profiling
- Add request latency middleware: log p50/p95/p99 per endpoint
- Add slow query logging (>500ms) for DB operations
- Track scraper execution time per source for performance regression detection
- Frontend: add Web Vitals reporting (LCP, FID, CLS)

---

## ~~v6 Sprint: QA System & Reliability~~ COMPLETED

### Test Suite (currently 0% coverage)
- **API unit tests** (pytest): test every router endpoint (happy path + error cases), test scorer logic with fixture data, test IP blocklist filtering, test store connector registry
- **API integration tests**: test scraper → scorer → opportunity pipeline end-to-end against test DB
- **Frontend tests** (vitest): test opportunity card rendering, keyboard navigation, API error states, settings page
- **Fixture factory**: seed test DB with realistic trend signals + opportunities for consistent test runs
- Coverage target: 80% for routers + scoring, 60% for scrapers (external API-dependent)

### Pre-Deployment Checks
- **GitHub Actions CI pipeline**: lint (ruff + eslint) → type check (mypy + tsc) → test (pytest + vitest) → build (next build) on every push/PR
- **Pre-commit hooks**: ruff format, ruff check, eslint, no secrets scanner (detect-secrets)
- **Migration safety check**: verify Alembic migrations are reversible before merge
- **Dependency audit**: pip-audit + npm audit on every CI run, fail on critical CVEs
- **Docker build verification**: ensure API + web containers build successfully

### Post-Deployment Checks
- **Smoke test suite**: after deploy, hit `/health`, `/opportunities/`, `/trends/summary` and verify 200 responses
- **Database migration verification**: confirm schema matches expected state post-deploy
- **Scraper canary**: trigger one Google Trends scrape and verify signals land in DB
- **Frontend canary**: headless browser (Playwright) loads dashboard and verifies opportunities render

### Health Checks & Monitoring
- Upgrade `/health` endpoint: check Postgres connectivity, Redis ping, storage reachability (currently returns static JSON without checking anything)
- Add `/health/detailed` endpoint: per-service status with latency measurements
- Add readiness probe (DB connected + migrations current) vs liveness probe (process alive)
- Startup validation: fail fast if SECRET_KEY is default, DB unreachable, or required env vars missing

### Alerting & Notifications
- **Service down detection**: Celery beat task pings all services every 60s, alerts on 3 consecutive failures
- **Scraper failure alerts**: if any scraper returns 0 signals for 2 consecutive runs, send notification
- **Error rate alerting**: if API 5xx rate exceeds 5% over 5min window, alert
- **Notification channels**: email via Resend (already a dependency), webhook for Slack/Discord
- **Alert dashboard**: dedicated `/alerts` page showing recent incidents, uptime, and resolution status

### Error Handling & Recovery
- Add FastAPI exception handlers for 404, 422, 500 with structured JSON error responses (currently unhandled exceptions return raw stack traces)
- Add `error.tsx` error boundaries in Next.js for graceful frontend error recovery
- Add `loading.tsx` Suspense fallbacks for every route
- Implement circuit breaker for external APIs (Etsy, Reddit, etc.) — stop calling after 5 failures, retry after 60s
- Add dead-letter queue for failed Celery tasks with manual retry from dashboard

### Observability
- Actually wire up OpenTelemetry (packages installed but zero instrumentation)
- Add request tracing: correlation IDs across API → Celery → storage
- Add structured request logging middleware: method, path, status, latency, request_id on every request
- Export metrics to Prometheus-compatible endpoint: request count, latency histogram, active DB connections, scraper signal counts

---

## v7 Sprint: Two-Sided Marketplace — Sellers & Printers

**Priority: Future (post-profitability) — build this AFTER solo Forge is generating revenue**

> **Viability analysis (2026-04-24):** The full two-sided marketplace has a cold
> start problem (need sellers AND printers simultaneously), fintech complexity
> (Stripe Connect, tax reporting, disputes), and competes with established players
> (Craftcloud, Shapeways, Treatstock). Solo Forge with one P1S can generate
> $1,000-1,700/mo at 57% margins from week 1, while the marketplace needs months
> of development + user acquisition before dollar one.
>
> **Recommended path:** Start solo → prove the product engine → hit capacity →
> add trusted friends as overflow printers (v3 scope) → only then consider
> opening as a public marketplace. The v3 "distributed printer network" sprint
> covers 80% of the value with 20% of the complexity. Build v7 only after
> you have 50+ orders/month and multiple printers maxed out.
>
> **Phase the rollout:**
> - Phase A (v3): Invite-only printer network — you're the only seller, friends print overflow
> - Phase B (v7-lite): Open printer signups — vetted printers, you still control the catalog
> - Phase C (v7-full): Open seller signups — full two-sided marketplace with public onboarding

### Concept

Forge becomes a two-sided marketplace with three roles:

- **Admin** (you) — operates the platform, manages both sides, sees everything
- **Sellers** — connect marketplace accounts (Etsy, Shopify, etc.), create listings, generate orders. They never touch a printer.
- **Printers** — own 3D printers, browse a job queue, accept jobs that match their hardware, print and ship for a payout. They never touch a marketplace.

The Forge backend orchestrates matching, payouts, quality control, and dispute resolution between both sides.

### User Flows

**Printer Onboarding:**
1. Signs up → creates profile (name, location, shipping zip)
2. Adds printer(s): brand, model, build volume, nozzle sizes, supported materials
3. Sets filament inventory: colors/materials on hand, auto-updates as jobs complete
4. Sets preferences: minimum payout per job ($), max print time, preferred categories, shipping radius
5. Sees a personalized job queue filtered by compatibility + preferences

**Seller Onboarding:**
1. Signs up → creates profile (shop name, business info)
2. Connects marketplace account(s) via store connectors (already built)
3. Uploads/generates designs (STL/3MF) with print specs (material, color options, infill, supports)
4. Sets retail price → platform calculates printer payout after fees
5. Orders flow in from connected stores automatically

**Job Lifecycle:**
```
Order received → Job created → Queued (matching) → Offered to compatible Printers
→ Printer accepts → Printing → QA photo upload → Shipped (tracking entered)
→ Delivered → Payout released (after return window)
```

### Data Model Changes

**Modified tables:**

`operator` — add:
- `role` expanded: "admin" | "seller" | "printer" (currently "owner" | "printer_operator")
- `display_name`, `avatar_url`, `location_zip` (nullable)
- `stripe_connect_id` (nullable, for printer payouts)
- `onboarding_completed` (bool, default false)
- `preferences_json` (nullable): min_payout_c, max_print_time_hrs, preferred_categories, shipping_radius_miles

`printer` — add:
- `brand` (string — "bambu", "prusa", "creality", "elegoo", etc.)
- `nozzle_sizes_json` (list of floats, e.g. [0.4, 0.6])
- `supported_materials_json` (list, e.g. ["PLA", "PETG", "TPU"])
- `max_build_mm_json` (e.g. {"x": 256, "y": 256, "z": 256})
- `hourly_rate_c` (int, printer's cost per hour — used for payout calculation)
- `is_available` (bool, default true — printer can toggle availability)

`order` — add:
- `seller_id` (FK to operator)
- `printer_operator_id` (FK to operator, nullable — assigned when accepted)
- `commission_c` (int — platform fee in cents)
- `printer_payout_c` (int — what the printer earns)

**New tables:**

`job_offer` — when a job is created, it's offered to N compatible printers
- id, print_job_id (FK), printer_operator_id (FK), offered_at, expires_at
- status: "pending" | "accepted" | "declined" | "expired"
- payout_c (int — what this printer would earn)

`payout` — tracks money owed/paid to printers
- id, printer_operator_id (FK), print_job_id (FK)
- amount_c (int), status: "pending" | "hold" | "released" | "paid"
- hold_until (timestamptz — release after return window, e.g. 7 days)
- stripe_transfer_id (nullable)
- created_at

`design_spec` — print requirements attached to each design
- id, design_id (FK)
- material_required (string, e.g. "PLA")
- color_options_json (list of hex codes)
- infill_pct (int, default 20)
- supports_required (bool)
- min_wall_mm (float)
- estimated_grams (float)
- estimated_time_minutes (int)
- min_build_x_mm, min_build_y_mm, min_build_z_mm (ints)

`shipment` — tracks shipping per job
- id, print_job_id (FK), carrier, tracking_no, label_url
- shipped_at, delivered_at
- cost_c (int — shipping cost)

### Pricing & Payout Model

```
Retail price (set by Seller)                           $25.00
  - Marketplace fee (Etsy ~6.5%, Shopify ~2.9%)        -$1.63
  - Platform fee (Forge, configurable, default 15%)    -$3.75
  - Shipping cost (from carrier API)                   -$4.50
  = Printer payout                                     $15.12
```

- Payouts held for 7 days after delivery (return window)
- Released automatically if no dispute
- Stripe Connect for actual money movement (future — start with manual tracking)
- Minimum payout threshold: $5.00 per job (configurable by printer)

### Job Matching Algorithm

When an order comes in:
1. Look up the design's `design_spec` (material, build volume, color)
2. Query all printers where:
   - `is_available = true`
   - `supported_materials_json` contains required material
   - `max_build_mm_json` fits the design dimensions
   - Printer has the required color in `filament_spool` inventory
   - Printer's `preferences_json.min_payout_c` <= calculated payout
   - Printer's `preferences_json.max_print_time_hrs` >= estimated time
   - Printer's `preferences_json.shipping_radius_miles` covers the buyer's zip (if set)
3. Rank by: past success rate > proximity to buyer > queue depth > hourly rate
4. Create `job_offer` rows for top 3-5 printers
5. First to accept gets the job (offers expire after 4 hours)
6. If no one accepts, re-offer to next batch or alert admin

### UI — Printer Dashboard

**Job Queue** (`/jobs`)
- Filterable list of available jobs matching the printer's capabilities
- Each job card shows:
  - Product thumbnail (render from design)
  - Material & color required
  - Estimated print time & filament usage (grams)
  - Payout amount (after all fees)
  - Shipping destination (city/state only, no full address until accepted)
  - Compatibility badges: printer model match, material match, color match
  - "Accept Job" button with payout confirmation
- Filters: min payout, material, print time, sort by (payout, time, newest)

**My Jobs** (`/my-jobs`)
- Accepted jobs in progress: status timeline (accepted → printing → QA → shipped)
- Upload QA photo (required before marking as shipped)
- Enter tracking number → auto-notifies seller and buyer
- Payout status per job (hold → released → paid)

**Printer Profile** (`/profile`)
- Edit printers: add/remove, update specs and availability
- Filament inventory management: add spools, track usage
- Payout preferences: minimum per job, preferred categories
- Earnings summary: total earned, pending, paid out

### UI — Seller Dashboard

- Existing Forge dashboard (opportunities, designs, listings)
- New: **Orders** page enhanced with fulfillment status from printer side
- New: tracking auto-populated when printer ships
- New: earnings/cost breakdown per order (retail - fees - payout = margin)

### UI — Admin Dashboard

- Everything both sides see, plus:
- **Operator management**: view all sellers and printers, approve/suspend accounts
- **Job oversight**: see all jobs, reassign, resolve disputes
- **Platform financials**: total GMV, total fees collected, total payouts, margin
- **Matching health**: acceptance rate, avg time to accept, expiration rate

### Security & Trust

- Printers never see buyer PII (name, full address) until they accept a job
- After acceptance: shipping label generated server-side, printer gets label PDF (not raw address)
- QA photo required before shipping — prevents empty box fraud
- Seller can dispute within 7 days of delivery → payout held during review
- Admin can force-release or force-refund any payout
- Rate limiting on job acceptance (prevent one printer from hoarding)
- Printer reputation score based on: on-time rate, QA pass rate, dispute rate

### Sprint Sequencing (6 weeks)

| Week | Deliverable |
|------|-------------|
| 1 | Expand operator model (roles, preferences, onboarding), design_spec table, job_offer table |
| 2 | Payout + shipment tables, pricing engine (retail → payout calculation), job matching algorithm |
| 3 | Printer dashboard: job queue, accept flow, profile/printer management |
| 4 | Seller dashboard enhancements: order fulfillment tracking, cost breakdown |
| 5 | Admin dashboard: operator management, job oversight, platform financials |
| 6 | QA photo upload flow, dispute handling, payout hold/release logic, integration testing |

### Files to create/modify
- Modified: `apps/api/app/models/operator.py` — expanded roles, preferences, stripe
- Modified: `apps/api/app/models/printer.py` — brand, materials, nozzle, availability
- Modified: `apps/api/app/models/order.py` — seller_id, printer_operator_id, commission, payout
- New: `apps/api/app/models/job_offer.py`
- New: `apps/api/app/models/payout.py`
- New: `apps/api/app/models/design_spec.py`
- New: `apps/api/app/models/shipment.py`
- New: `apps/api/app/services/pricing.py` — payout calculator
- New: `apps/api/app/services/matcher.py` — job matching algorithm
- New: `apps/api/app/routers/jobs.py` — printer-facing job queue + accept
- New: `apps/api/app/routers/payouts.py` — payout tracking
- New: `apps/web/src/app/jobs/` — printer job queue UI
- New: `apps/web/src/app/my-jobs/` — printer active jobs UI
- New: `apps/web/src/app/profile/` — printer profile management
