# Forge — Claude Code Build Prompt

> Paste everything below into Claude Code as your initial brief. Start with the "How to use this brief" section.

---

## How to use this brief

You are Claude Code. Your job is to build **Forge**, a production system described below. Before writing any code:

1. Read the entire brief end-to-end.
2. Ask me the clarifying questions listed in §13. Do not assume answers — my answers materially change architecture.
3. Produce a one-page implementation plan (components, order of build, estimated LOC per module) and wait for me to approve it.
4. Only then start building, following the milestones in §10. After each milestone, pause, run the acceptance tests, and summarize what works before moving on.
5. Commit often with clear messages. Keep a `DECISIONS.md` log for every non-trivial trade-off you make.

Do not silently skip scope. If something in this brief is ambiguous or impossible, surface it and propose an alternative.

---

## 1. Mission & north-star metric

**Forge is an autonomous product R&D, manufacturing, and fulfillment system for a Bambu Lab 3D-printing micro-business.** It discovers rising product trends, generates or sources printable designs, lists them on marketplaces, routes incoming orders to a printer farm, and ships them — with a human only in the approval loop.

**Primary purpose: profit.** Every subsystem exists to improve one number:

> **North-star: weekly net margin $ = revenue − (material + electricity + platform fees + shipping + labor minutes × $/min).**

Forge is not a hobby dashboard. Features that do not plausibly move the north-star within 90 days are out of scope for v1.

**Target unit economics (tune with real data):**
- Gross margin per unit: **45–65%**
- Payback on each new SKU (designed → profitable): **< 30 days**
- Human touch time per order: **< 90 seconds**
- Print-farm utilization: **> 60%** of available hours

---

## 2. Business model

Forge runs on three revenue loops, in priority order:

1. **Evergreen catalog** — SKUs the trend engine identified, we designed, and they sell reliably week over week. This is the cash engine.
2. **Trend sprints** — 2–4 week windows around rising searches (seasonal, viral, niche). High margin, short tail.
3. **Bespoke / prompt-to-print** — customer types a request; an AI pipeline generates a custom model and prices it. Highest margin, lowest volume.

Revenue surfaces: **Etsy** (primary marketplace — our storefront), **Shopify** (owned storefront, same SKUs), **MakerWorld/Printables** (paid model downloads as secondary royalty stream). Do **not** build TikTok Shop, Amazon, or eBay integrations in v1 — scope creep.

---

## 3. System architecture

```
 ┌───────────────────┐   ┌────────────────────┐   ┌─────────────────┐
 │ Trend Intelligence│──▶│ Opportunity Scorer │──▶│ Design Pipeline │
 │  (scrapers+APIs)  │   │   (LLM + rules)    │   │ (gen / remix)   │
 └───────────────────┘   └────────────────────┘   └────────┬────────┘
                                                           │
                         ┌─────────────────────────────────▼─────────┐
                         │   Printability & QA Gate                  │
                         │   (mesh repair, overhangs, wall, time)    │
                         └────────────────────┬──────────────────────┘
                                              │
                     ┌────────────────────────▼────────────────────┐
                     │ Listing Generator (copy + images + price)   │
                     └────────────────────────┬────────────────────┘
                                              │
                         ┌────────────────────▼────────────┐
                         │  Approval Dashboard (human UI)  │
                         └────────────────────┬────────────┘
                                              │ (approve)
                     ┌────────────────────────▼────────────────────┐
                     │   Marketplace Publisher (Etsy + Shopify)    │
                     └────────────────────────┬────────────────────┘
                                              │ (order webhook)
 ┌──────────────┐        ┌───────────────────▼────────────┐       ┌──────────────────┐
 │ Bambu Farm   │◀───────│ Order Intake & Job Router      │──────▶│ Fulfillment +    │
 │ (MQTT + cam) │        │  (slice, queue, assign)        │       │ shipping labels  │
 └──────┬───────┘        └────────────────────────────────┘       └──────────────────┘
        │
        ▼
 ┌──────────────────────────┐
 │ Telemetry + Vision QA    │─────▶ Analytics & Feedback Loop ─────▶ back into Scorer
 └──────────────────────────┘
```

Everything writes to a single Postgres; Redis handles queues; object storage (S3 or Cloudflare R2) holds models, renders, and time-lapses.

---

## 4. Core components (build these)

### 4.1 Trend Intelligence Service

**Purpose:** produce a daily-refreshed ranked list of demand signals.

**Sources (v1):**
- **MakerWorld** and **Printables** — scrape trending, new, most-downloaded, most-liked (respect rate limits; cache aggressively). No API, so use Playwright with a polite `User-Agent` and randomized backoff.
- **Etsy** — official API for listing search; pull top/rising for target queries ("desk organizer", "planter", "cable management", etc.). Track listing count vs. review velocity as a proxy for supply/demand gap.
- **Google Trends** — via `pytrends` (unofficial but stable).
- **Reddit** — r/functionalprint, r/3Dprinting, r/BambuLab hot posts via the official API.
- **Pinterest trends** — public trends endpoint.
- **TikTok** — scrape hashtag search for `#3dprint #etsyseller #functionalprint` (read-only, no posting).

**Outputs:** `trend_signal` rows with `{source, query/topic, velocity, volume, geography, captured_at, raw_payload_s3_key}`.

**Rules:** each scraper is isolated, runs on a schedule, fails closed (one broken source doesn't kill the pipeline), and stores the raw HTML/JSON so we can reprocess without re-scraping.

### 4.2 Opportunity Scoring Engine

**Purpose:** turn noisy trend signals into a ranked backlog of product ideas worth making.

**Inputs:** raw `trend_signal` rows from §4.1, plus our own sales history from §4.11.

**Pipeline:**
1. **Cluster** signals across sources into product concepts (semantic clustering via embeddings in pgvector).
2. **Demand score** — weighted blend of search velocity, listing-click-through proxies, subreddit upvote rate, and Etsy review-per-day.
3. **Competition score** — Etsy listing count for the concept, median price, median review count. Low supply + high demand = gold.
4. **Printability prior** — LLM (Claude) estimates print feasibility on a Bambu X1C/P1S from the concept description alone (size, mechanical complexity, multi-material need).
5. **Margin estimate** — rough BOM (grams of filament × $/kg) vs. median market price × (1 − Etsy fees).
6. **IP / brand filter** — reject anything that looks like Disney, Pokémon, Nintendo, pro sports, or other IP-loaded brands. Maintain a blocklist + LLM double-check.
7. **Composite score** = demand × margin × (1/competition) × printability × IP_safe. Store with explanations.

**Output:** `opportunity` table, ranked, with a short LLM-written rationale per row.

### 4.3 Design Generation Pipeline

**Purpose:** turn an approved opportunity into a printable `.3mf` or `.stl` file we legally own or can commercially use.

**Three paths, try in order:**

**a) Parametric generation (preferred).** For common categories (planters, organizers, hooks, brackets, holders, cookie cutters, Gridfinity bins), maintain a library of **OpenSCAD** or **CadQuery** templates parameterized by size, style, motif. The LLM fills in parameters from the opportunity description. Fastest, fully ownable, free to commercialize.

**b) Remix of permissively-licensed models.** Search MakerWorld / Printables / Thingiverse filtered strictly to `CC0`, `CC-BY`, or `CC-BY-SA` with explicit commercial-use allowance. Record license + attribution metadata with every remix. Apply non-trivial modifications (not just rescaling). **Never** touch `CC-BY-NC`, `CC-BY-ND`, or any model without an explicit license.

**c) Text-to-3D AI generation.** Use Meshy, Tripo, or Rodin (pick one based on quality/cost benchmarking you run in milestone M2). Only for concepts where (a) and (b) fail. Mesh output quality is the bottleneck — expect to reject 60%+.

**All paths feed §4.4.**

### 4.4 Printability & QA Gate

**Purpose:** reject garbage before it wastes filament or ruins a listing.

**Checks:**
- **Mesh integrity** — manifold, no holes, no non-manifold edges, no self-intersections. Auto-repair with `trimesh` / `pymeshlab`; reject if repair fails.
- **Bounding box** fits Bambu X1C/P1S build plate (256×256×256 mm). If larger, auto-scale or reject.
- **Min wall thickness** ≥ 1.2 mm (configurable per filament).
- **Overhang analysis** — % of surface > 45°. If high, flag for supports (cost).
- **Slicer dry-run** — invoke Bambu Studio / OrcaSlicer CLI to produce a `.gcode.3mf` and extract: estimated print time, filament grams by color, support material grams, max layer-change count.
- **Cost estimate** — filament_g × $/g + time_hr × kWh_per_hr × $/kWh + amortized wear ($/hr). Store per SKU.
- **Photogenic check** — render 6 turntable views with a headless Blender script; LLM scores visual appeal 0–10. Ugly designs don't sell no matter how functional.

**Output:** pass/fail + full cost/time/render manifest attached to the opportunity.

### 4.5 Listing Generator

**Purpose:** produce marketplace-ready copy and imagery for every approved design.

**Produces:**
- **Title** — SEO-optimized, within Etsy's 140-char limit, front-loads keywords.
- **Description** — features, dimensions, material options, print time, care instructions, shipping estimate. Honest; no weasel claims.
- **Tags** — Etsy 13-tag limit, derived from trend signals that actually drove the opportunity.
- **Price** — from §4.4 cost × (1 + margin_target) × competition-adjustment. Never below cost + 40%. Round to psychological price points.
- **Hero images (5–8)** — Blender turntable renders composited onto lifestyle backgrounds via an image model (Nano Banana, Flux, or SDXL). One plain white-bg render required; rest are contextual lifestyle shots (desk, kitchen, garden, etc. based on category). Watermark only on site previews, not sold assets.
- **Variants** — color options derived from on-hand filament inventory (§4.9).

Written via Claude with a house-style prompt that enforces tone, banned words (no "amazing," "perfect," etc.), and compliance with Etsy policies.

### 4.6 Approval Dashboard (human-in-the-loop)

**Purpose:** me, the operator, reviews and ships product decisions in under a minute each.

**Stack:** Next.js (App Router) + Tailwind + shadcn/ui + tRPC or server actions to the Postgres.

**Screens:**
1. **Opportunity queue** — ranked list with scorecard, LLM rationale, thumbnail. Actions: *design this / skip / blacklist topic*.
2. **Design review** — turntable render, printability report, cost breakdown, generated listing preview. Actions: *approve & publish / request revision / reject*.
3. **Live farm** — printer status, current jobs, webcam tiles, ETA, failures.
4. **Orders** — incoming order feed, status (queued, printing, packed, shipped), exceptions.
5. **Finance** — weekly revenue, cost, margin, P&L per SKU, top/bottom performers.

Keyboard-first navigation (`J/K` to move, `A` approve, `R` reject, `E` edit). Log every human action with reason for the feedback loop (§4.11).

### 4.7 Marketplace Publisher

**Purpose:** push approved listings live and keep them synced.

- **Etsy API v3** — create/update/delete listings, manage inventory, variants, images. Handle OAuth refresh. Respect rate limits.
- **Shopify Admin API** — same listings mirrored to the owned storefront.
- **Idempotency** — every publish keyed on internal SKU UUID; retries don't duplicate.
- **Inventory sync** — single source of truth is Forge's Postgres; Etsy/Shopify are slaves.
- **Takedown command** — one click pulls a SKU from all marketplaces (for IP complaints, defects, or end-of-life).

### 4.8 Order Intake & Job Router

**Purpose:** take an order webhook and turn it into a print job on the right printer.

Flow: webhook → validate → resolve SKU to `.3mf` + slicer profile + filament colors → check inventory → reserve filament → assign to the printer with shortest estimated queue → enqueue MQTT start command → update order status.

Edge cases to handle explicitly: color not in stock (pause order + alert), file missing (alert), all printers offline (queue with SLA clock), duplicate webhook (idempotent).

### 4.9 Bambu Printer Farm Controller

**Purpose:** command and observe N Bambu printers; target hardware = Bambu X1C/P1S, AMS required.

**Integration:**
- Use `bambulabs-api` Python lib (or equivalent) over local MQTT. Fall back to Bambu cloud only if LAN unavailable.
- Respect Bambu's authorization controls (2025+) — use developer mode / LAN-only mode where possible; document the exact setup steps in `README.md`.
- Per printer: start job, pause, resume, cancel, read status, read AMS slot contents, read camera stream (RTSP or pulled JPEG snapshots).

**Filament inventory:** read AMS RFID tags where present, otherwise maintain manual `filament_spool` table (color, material, grams_remaining, cost/gram). Decrement on every completed print using slicer estimate × 1.05 waste factor.

**Vision QA (stretch, but cheap to add):** every 60 s, pull a frame from each printing bed, pass to Claude/GPT-4V with a fixed prompt ("classify: OK / spaghetti / layer_shift / adhesion_fail / other"); if failure confidence > 0.8, auto-pause and alert.

### 4.10 Fulfillment & Shipping

**Purpose:** close the loop from "print done" → "package in the mail".

- **Shippo** or **EasyPost** API for label generation. Pick one in M3 based on the cheaper rate for small parcels.
- On print completion: generate label, attach tracking to order, update marketplace with tracking #, email customer.
- **Packing station UI** — scan SKU barcode, prints label + packing slip. Human inserts print in bag/box, slaps label, drops in mail bin. Target: < 45 s per order.
- **Returns** — simple RMA flow in dashboard; refund via marketplace API.

### 4.11 Analytics & Feedback Loop

**Purpose:** close the learning loop — what sells, what flops, why.

Every SKU tracks: impressions, clicks, conversions, revenue, cost, margin, return rate, review score, time-to-first-sale. Roll up daily.

**Feedback into §4.2:**
- SKUs that hit margin target in < 14 days → boost similar opportunities.
- SKUs that get returns or bad reviews → diagnose (printability? description? photo?) and down-weight the pattern.
- Weekly LLM retro: "Here are last week's wins/losses with data. Write a 10-bullet memo on what patterns we should reinforce or avoid next week." Operator reads it over coffee.

### 4.12 Finance & Reporting

- Every cost event (filament, electricity, shipping, platform fee, refund) lands in a `ledger` table.
- Weekly P&L, per-SKU P&L, cash flow. CSV export for bookkeeping.
- Sales-tax tracking per state/country (US + EU VAT for Etsy sellers).

---

## 5. Data model (key tables — not exhaustive)

```
trend_signal            (id, source, query, velocity, volume, captured_at, raw_s3_key)
opportunity             (id, concept, score, demand, competition, printability, margin_est,
                         rationale_md, ip_status, status, created_at)
design                  (id, opportunity_id, source_path ['parametric'|'remix'|'aigen'],
                         license, license_attribution, model_s3_key, created_at)
qa_report               (id, design_id, pass, checks_json, time_s, filament_g, cost_estimate_c)
render                  (id, design_id, angle, image_s3_key, style)
listing                 (id, design_id, sku, title, description_md, tags, price_c,
                         status, etsy_listing_id, shopify_product_id, created_at)
filament_spool          (id, material, color, hex, grams_remaining, cost_c_per_g,
                         ams_slot, printer_id)
printer                 (id, model, serial, ip, status, last_seen)
print_job               (id, printer_id, order_id, design_id, gcode_s3_key,
                         status, started_at, completed_at, filament_used_g)
order                   (id, marketplace, external_id, sku, customer_hash, variant_json,
                         price_c, cost_c, status, created_at, shipped_at, tracking_no)
ledger                  (id, ts, type, amount_c, ref_id, ref_table, note)
human_action            (id, ts, user, screen, target_id, action, reason)
```

All money in **integer cents**, all times in UTC. Soft-delete everywhere.

---

## 6. Tech stack

Pin these unless you have a strong reason:

- **Backend:** Python 3.12, FastAPI, SQLAlchemy + Alembic, Celery (Redis broker), Playwright (scrapers), `trimesh`/`pymeshlab` (geometry), `cadquery` + OpenSCAD (parametric), Blender headless (rendering).
- **Frontend:** TypeScript, Next.js 15 App Router, Tailwind, shadcn/ui, TanStack Query, Zod, tRPC.
- **DB:** Postgres 16 + `pgvector`.
- **Cache/queue:** Redis 7.
- **Object storage:** Cloudflare R2 (S3-compatible, no egress fees).
- **LLM:** Claude (Anthropic API) for reasoning, copy, vision QA. Use the latest Sonnet for hot paths, Haiku for cheap classification, Opus only when quality matters.
- **3D gen:** Meshy API (evaluate Tripo + Rodin in M2).
- **Image gen:** pick one of Flux Pro, SDXL, or Nano Banana based on cost/quality bench in M2.
- **Marketplace:** Etsy Open API v3, Shopify Admin API 2025-10.
- **Shipping:** Shippo (default) or EasyPost.
- **Printer control:** `bambulabs-api` over MQTT.
- **Deploy:** Fly.io (web + workers), Neon or Supabase (Postgres), Upstash (Redis). Printer controller runs on a local NUC/Pi on the same LAN as the printers.

Every external API key in env vars, rotated through a `secrets/` layer so we can swap providers without refactors.

---

## 7. External integrations & docs

List of APIs to integrate and their docs (look up the latest URLs yourself when building):

- Anthropic Claude API — messages + vision.
- Etsy Open API v3 — listings, inventory, orders, shop receipts.
- Shopify Admin API — products, orders, fulfillments.
- Meshy API — text-to-3D.
- Shippo API — shipping labels + tracking.
- Bambu Lab MQTT — local printer protocol (via `bambulabs-api`).
- `pytrends` — Google Trends.
- Reddit official API (OAuth).
- MakerWorld / Printables — scraping only; no public API. Respect their ToS and robots.txt; if ToS forbids scraping, route those sources through legitimate RSS/feeds or drop them.

---

## 8. Legal, ethical, and operational guardrails

Non-negotiable — violations get us banned from marketplaces or sued:

1. **IP:** hardcoded blocklist of brands/franchises (Disney, Pokémon, Marvel, DC, Nintendo, Star Wars, pro sports leagues, known designer brands). LLM double-check on every opportunity. If score is uncertain, it's rejected.
2. **Model licenses:** only `CC0`, `CC-BY`, `CC-BY-SA`, or explicitly-commercial-OK licenses for remixes. Store the license text + source URL + author with every design. Emit attribution in listing descriptions where license requires it.
3. **Marketplace ToS:** read Etsy's handmade / reseller policies; tag SKUs as "made by me" only when we actually printed them. Don't misrepresent.
4. **Safety claims:** no food-contact, toy-for-kids-under-3, or medical/therapeutic claims unless we've actually tested and certified. Default listing boilerplate explicitly disclaims these.
5. **Customer data:** never log full names/addresses in non-encrypted stores. PII lives in Postgres with column-level encryption; hashes in analytics.
6. **Rate limiting & politeness:** every scraper respects `robots.txt`, uses a clearly identifying `User-Agent`, and backs off on 429.
7. **Tax:** track Etsy's automatically-collected sales tax separately from revenue in the ledger.

---

## 9. Profit-first defaults

Use these unless overridden:

- Reject opportunities with estimated margin < 40%.
- Reject designs with estimated print time > 6 hours unless price > $60.
- Prefer PLA/PETG over exotic filaments (cheaper, faster, fewer failures).
- Prefer single-color prints; only go multi-color if margin justifies AMS swaps + time.
- Batch orders for the same SKU into one plated print when possible (Orca/Bambu supports arrange-all-objects).
- Auto-pause listings whose 30-day return rate > 8% — something's wrong.
- Cap ad spend at 0 in v1. Ranking on organic SEO only until we have data.

---

## 10. Build milestones

Each milestone ends with a demo-able state. Don't skip ahead.

**M0 — Skeleton (day 1)**
- Monorepo bootstrapped: `apps/api`, `apps/web`, `apps/printer_controller`, `packages/shared`.
- Postgres + Redis + R2 provisioned via `docker compose` locally.
- Auth for operator dashboard (single-user email magic link via Resend).
- CI green, type checks clean, `make dev` launches everything.

**M1 — Trend + opportunity (week 1)**
- Trend scrapers for MakerWorld, Printables, Etsy, Google Trends working on cron.
- Opportunity scorer producing ranked table.
- Dashboard screen 1 (opportunity queue) functional.
- **Acceptance:** operator sees a fresh ranked list of 20+ opportunities every morning, each with rationale and score.

**M2 — Design + QA (week 2–3)**
- Parametric generation working for 5 categories (Gridfinity bin, planter, hook, phone stand, cookie cutter).
- Remix pipeline with license validation.
- Text-to-3D integration with one provider (after cost benchmarking).
- Printability gate (mesh repair, slicer CLI, cost estimate, Blender render).
- Dashboard screen 2 (design review).
- **Acceptance:** operator approves a design → file on disk + cost + renders, end-to-end in < 90 s.

**M3 — List + order (week 4)**
- Listing generator (copy + tags + price).
- Etsy publisher (sandbox first, then live).
- Shopify publisher.
- Order webhook intake → persisted → dashboard.
- **Acceptance:** approved design goes live on Etsy sandbox in one click; test order flows back into dashboard.

**M4 — Print + ship (week 5–6)**
- Bambu controller on local box talking to at least one printer over MQTT.
- Order → slice → assign → print → complete flow.
- Shippo label generation on print complete.
- Dashboard screens 3 (farm) and 4 (orders).
- **Acceptance:** test order → print starts automatically on real printer → label generated when done → tracking pushed to marketplace.

**M5 — Analytics + loop (week 7)**
- Per-SKU analytics.
- Weekly P&L + retro memo.
- Feedback weights fed back into scorer.
- Dashboard screen 5 (finance).
- **Acceptance:** after a week of live data, scorer demonstrably reweights based on what sold.

**M6 — Harden & scale (week 8)**
- Vision QA on camera feeds.
- Multi-printer support proven with 2+ printers.
- Backup + restore playbook.
- Runbook for common failures.
- **Acceptance:** operator can leave the system alone for 48 hours and return to a still-working shop.

---

## 11. Acceptance criteria (overall)

Forge v1 is "done" when **all** of these are true:

- [ ] Running autonomously for a continuous 14-day period with the operator spending ≤ 30 min/day.
- [ ] At least 20 SKUs live across Etsy + Shopify.
- [ ] At least 15 orders fulfilled end-to-end with no manual slicing.
- [ ] Positive gross margin on ≥ 80% of shipped orders.
- [ ] No IP complaints, no marketplace policy strikes, no negative reviews caused by system error (vs. material/print variance).
- [ ] P&L dashboard reconciles to marketplace payouts within ±1%.
- [ ] Documented, containerized, with a runbook a competent sysadmin could operate.

---

## 12. Anti-goals (explicitly out of scope for v1)

- No mobile app.
- No customer-facing AI chat.
- No multi-tenant / SaaS. Single operator, single business.
- No computer-vision auto-recovery beyond pause-and-alert.
- No physical robotics (pick-and-place arm, conveyor, etc.).
- No crypto, no NFTs, no "print-to-earn".
- No TikTok/Amazon/eBay integration.
- No generative image try-on or AR preview.
- No custom slicer. Use Bambu Studio / OrcaSlicer CLI.

If a feature feels exciting but isn't on §4 or §10, write it in `FUTURE.md` and move on.

---

## 13. Questions for me before you start

Answer these and I'll reply; then produce the plan in §"How to use this brief" step 3.

1. **Printers on hand right now:** how many Bambu units, which models (X1C / P1S / A1), AMS or not?
2. **Existing accounts:** do I already have Etsy seller, Shopify, Shippo, Anthropic, Meshy accounts? Which am I missing?
3. **Hosting budget:** monthly cap I'm willing to spend on infra + API calls during the build?
4. **Geography:** where am I shipping from, and which countries am I willing to ship to in v1?
5. **Operator time per day** I'm willing to spend (affects how aggressive the automation defaults should be)?
6. **Filament inventory** — rough list of colors/materials on hand, or should we assume a blank slate?
7. **Risk appetite on remixes** — do I want to use CC-licensed remixes at all, or stick to fully-original parametric + AI-gen only?
8. **Brand/name for the shop** — or should we pick one together during M3?
9. **Any categories I want to exclude on principle** (e.g., no firearms accessories, no religious/political items, etc.)?
10. **Tax setup** — US sole prop, LLC, something else? Affects the ledger schema.

---

## 14. Working rules for you (Claude Code) while building

- Keep PRs under ~400 LOC; one module per PR.
- Tests: pytest for Python, Vitest for TS. Unit tests for every pure function; integration tests for every external API via recorded cassettes (VCR.py / MSW).
- Types everywhere. No `any`, no untyped Python defs.
- No secrets in code. All via env + `.env.example`.
- Every module has a `README.md` section explaining what it does, how to run it, and what could go wrong.
- If you hit an ambiguity I didn't specify, **ask**, don't guess. Budget yourself one question per blocking issue and batch them.
- Log like you're going to be debugging this at 2am in six months. Structured logs (JSON), request IDs, correlation IDs across services.
- Observability from day one: OpenTelemetry traces, Prometheus metrics, a `/health` per service.
- Every long-running job is idempotent and resumable. If the process dies mid-print-assignment, we pick up where we left off.
- Write a `DECISIONS.md` entry for each meaningful architectural choice: *what, why, alternatives considered, date*.

---

**End of brief. Start by reading, then asking §13.**
