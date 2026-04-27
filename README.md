# BigBRUH / SentinelForge

Production-oriented local deployment scaffold for a self-hosted **threat actor investigation and defensive disruption** platform.

## What is included
- FastAPI backend with:
  - health + readiness checks,
  - case intake/listing,
  - bulk entity ingestion,
  - persistent passive enrichment jobs,
  - evidence hashing + retrieval,
  - IOC export (JSON/CSV),
  - audit logging middleware,
  - optional API-key protection for non-health routes.
- React/Vite frontend starter for analyst workflows.
- Docker Compose stack with PostgreSQL, Redis (AOF), Neo4j, backend, frontend.
- Seed/demo data + safe-operations SOP + platform spec.

## Local production-like run

```bash
cp .env.example .env
# set API_KEY to a strong secret for non-dev use
docker compose -f infra/compose/docker-compose.yml up --build
```

Endpoints:
- API base: `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/healthz`
- Readiness: `http://localhost:8000/readyz`
- Frontend: `http://localhost:5173`

## Commands

```bash
make run      # start local stack
make test     # run backend tests
make check    # basic local runnability checks
```

## Auth behavior
- If `API_KEY` is blank, routes are open (dev mode).
- If `API_KEY` is set, provide `x-api-key` for protected `/api/v1/*` routes.

## Safety Boundaries
This project is **defensive-only** and excludes unauthorized access, exploit delivery, credential theft, persistence, ransomware/destructive actions, retaliation, doxxing, precise location tracking, and other offensive abuse capabilities.
