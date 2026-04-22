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
  - audit logging middleware.
- React/Vite frontend starter for analyst workflows.
- Docker Compose stack with PostgreSQL, Redis (AOF), Neo4j, backend, frontend.
- Seed/demo data + safe-operations SOP + platform spec.

## Local production-like run

```bash
cp .env.example .env
docker compose -f infra/compose/docker-compose.yml up --build
```

Endpoints:
- API base: `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/healthz`
- Readiness: `http://localhost:8000/readyz`
- Frontend: `http://localhost:5173`

## Backend tests (local)

```bash
PYTHONPATH=backend pytest -q backend/tests
```

## Safety Boundaries
This project is **defensive-only** and excludes unauthorized access, exploit delivery, credential theft, persistence, ransomware/destructive actions, retaliation, doxxing, precise location tracking, and other offensive abuse capabilities.
