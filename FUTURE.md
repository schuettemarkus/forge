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

---

## v4 Sprint: Security Hardening

**Priority: Critical — must complete before any production deployment**

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

## v5 Sprint: Performance & Speed

**Priority: High — essential for responsive dashboard and efficient resource usage**

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

## v6 Sprint: QA System & Reliability

**Priority: High — zero test coverage today, need automated quality gates**

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
