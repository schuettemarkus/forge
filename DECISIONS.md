# Forge — Architecture Decision Log

## D001: Monorepo over microservices (2026-04-24)
**What:** Single repo with apps/api, apps/web, apps/printer as co-located packages.
**Why:** Single operator, $50-100/mo budget. Microservices add networking, deployment, and debugging overhead that doesn't pay off at this scale.
**Alternatives:** Separate repos per service (rejected: coordination overhead), nx/turborepo monorepo (rejected: overkill for 3 apps).

## D002: FastAPI + Celery over Django (2026-04-24)
**What:** FastAPI for the API layer, Celery for async task processing.
**Why:** FastAPI's async support is better for webhook handling and concurrent scraping. Celery gives us retries, scheduling, and monitoring. Django's ORM and admin are nice but we're building our own dashboard anyway.
**Alternatives:** Django + Celery (rejected: heavier ORM, less async-native), FastAPI + ARQ (rejected: less mature than Celery).

## D003: pgvector in Postgres over dedicated vector DB (2026-04-24)
**What:** Use pgvector extension in our existing Postgres rather than Pinecone/Weaviate/etc.
**Why:** One fewer service to manage, free, and our vector workload (clustering trend signals) is small enough that pgvector handles it fine.
**Alternatives:** Pinecone (rejected: cost), ChromaDB (rejected: another process to manage).

## D004: Cloudflare R2 over S3 (2026-04-24)
**What:** R2 for object storage (models, renders, raw scrape data).
**Why:** S3-compatible API, no egress fees. We'll be serving renders to the dashboard frequently; egress-free saves money on a tight budget.
**Alternatives:** S3 (rejected: egress fees add up), local filesystem (rejected: not portable, no CDN).

## D005: LLC recommended for business entity (2026-04-24)
**What:** Recommended single-member LLC taxed as sole prop.
**Why:** Personal asset protection with minimal overhead (~$60 Utah filing fee). Can elect S-corp taxation later if revenue justifies it.
**Alternatives:** Sole prop (rejected: no liability protection), S-corp (rejected: premature overhead).

## D006: Single P1S printer, no Vision QA in M0-M4 (2026-04-24)
**What:** Design around one Bambu P1S without built-in camera. Vision QA deferred to M6 stretch goal requiring external USB/IP camera.
**Why:** P1S lacks the X1C's built-in chamber camera. Vision QA requires additional hardware investment.
**Alternatives:** Buy X1C (rejected: unnecessary cost for v1), skip vision QA entirely (rejected: keep it as stretch goal).
