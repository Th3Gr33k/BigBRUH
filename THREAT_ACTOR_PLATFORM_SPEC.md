# SentinelForge (Self-Hosted Threat Actor Investigation & Defensive Disruption Platform)

## 0) Safety Position and Scope
This specification is intentionally **defensive and lawful-only**.

It supports:
- lawful threat intelligence research,
- incident response,
- abuse reporting,
- defensive blocking,
- sinkholing on owned/authorized assets only,
- evidence preservation for legal/LE referral.

It **explicitly excludes** any unauthorized access or offensive abuse capability, including exploit delivery, malware/RAT deployment, credential theft, persistence on third-party systems, ransom/destructive behavior, doxxing, forced deanonymization, or precise live-location tracking.

---

## 1) Product Name Options
1. **SentinelForge** (recommended)
2. **AegisTrace**
3. **CaseGraph CTI**
4. **HarborIntel**
5. **NexusDefend Investigator**

---

## 2) Mission Outcomes
- Rapidly convert raw indicators into actionable, provenance-backed intelligence.
- Build evidence-quality case files with chain-of-custody and immutable audit records.
- Enable safe defensive disruption via abuse complaints, takedown coordination, IOC sharing, and internal blocklists.
- Provide LE-ready referral packages with confidence scoring and legal context.

Success KPIs:
- Mean Time to Enrichment (MTTE) < 5 minutes per indicator batch.
- Analyst case assembly time reduced by 60%.
- Complaint acceptance/takedown conversion rate tracked by provider.
- False-positive rate on auto-clustered campaigns < 8%.

---

## 3) Architecture (Production-Ready)

### 3.1 High-level Components
- **Frontend**: React + TypeScript + Vite, RBAC-aware portal.
- **API Layer**: FastAPI (REST + async jobs + authn/authz).
- **Task/Workflow Engine**: Celery workers + Redis broker.
- **Relational Store**: PostgreSQL (cases, evidence, users, audit, workflow state).
- **Graph Store**: Neo4j (infrastructure relationships, clustering, campaign topology).
- **Object Storage**: MinIO/S3-compatible for screenshots, captures, artifacts.
- **Search/Index**: PostgreSQL full-text (or optional OpenSearch extension).
- **Reporting Service**: HTML/PDF report renderer + STIX 2.1 exporters.
- **Connector Framework**: plugin-based enrichers/ingestors/reporters.
- **Observability**: Prometheus + Grafana + Loki.
- **Secrets**: Vault or Docker secrets.

### 3.2 Trust Zones
- **Zone A (DMZ)**: controlled collectors, URL fetcher, screenshot worker behind egress controls.
- **Zone B (Core App)**: API, frontend, Postgres, Redis.
- **Zone C (Sensitive Analysis)**: sandbox detonation lab (owned), graph analytics, evidence packager.
- **Zone D (Admin/SOC)**: SIEM connectors, admin tools.

### 3.3 Network Controls
- Egress allowlist for enrichment APIs.
- No direct inbound from worker nodes except broker/db as needed.
- mTLS service-to-service.
- Strictly isolated detonation and browser capture environment.

---

## 4) Data Model (PostgreSQL)

### 4.1 Core Tables
- `users(id, email, role, mfa_enabled, created_at)`
- `roles(id, name)`
- `cases(id, case_ref, title, status, severity, owner_id, created_at, updated_at)`
- `case_entities(id, case_id, entity_type, entity_value, normalized_value, first_seen, last_seen)`
- `observables(id, observable_type, value, tlp, confidence, source, created_at)`
- `evidence_items(id, case_id, kind, sha256, object_uri, mime_type, acquired_at, acquired_by, source_method)`
- `chain_of_custody(id, evidence_id, event_type, actor_id, timestamp, notes, prev_hash, record_hash)`
- `enrichment_results(id, observable_id, provider, raw_json, parsed_json, fetched_at, ttl_until)`
- `campaigns(id, name, confidence, summary, created_at)`
- `case_campaign_links(id, case_id, campaign_id, rationale)`
- `reports(id, case_id, report_type, version, object_uri, created_by, created_at)`
- `abuse_actions(id, case_id, target_type, target_value, status, submitted_at, provider_ticket_ref)`
- `retention_policies(id, data_class, retention_days, legal_hold_allowed)`
- `legal_holds(id, case_id, reason, opened_at, closed_at)`
- `audit_logs(id, actor_id, action, resource_type, resource_id, request_id, ip, user_agent, created_at)`

### 4.2 Constraints
- Unique normalized IOC constraints (`observable_type + value_hash`).
- Evidence rows immutable after sealing (append-only updates via new version records).
- Foreign-key and ON DELETE RESTRICT for evidence/legal records.

---

## 5) Graph Model (Neo4j)

### 5.1 Node Labels
- `:Domain`, `:IP`, `:URL`, `:Email`, `:Phone`, `:Wallet`, `:Cert`, `:ASN`, `:Host`, `:FileHash`, `:KitArtifact`, `:Campaign`, `:Case`, `:Report`, `:Org`.

### 5.2 Relationship Types
- `(:Domain)-[:RESOLVES_TO {first_seen,last_seen}]->(:IP)`
- `(:Domain)-[:REGISTERED_WITH]->(:Registrar)`
- `(:URL)-[:HOSTED_ON]->(:Domain)`
- `(:Domain)-[:USES_CERT]->(:Cert)`
- `(:Wallet)-[:CO_OCCURS_WITH]->(:Wallet)`
- `(:FileHash)-[:DELIVERED_BY]->(:URL)`
- `(:Entity)-[:ATTRIBUTED_TO {confidence, rationale}]->(:Campaign)`
- `(:Case)-[:CONTAINS]->(:Entity)`
- `(:Case)-[:REFERENCES]->(:Campaign)`

### 5.3 Graph Analytics
- Connected components for infra clusters.
- Similarity scoring from reused cert metadata, NS records, favicon hash, page title, wallet reuse.
- Time-sliced subgraph snapshots for timeline reconstruction.

---

## 6) API Design (FastAPI)

### 6.1 Auth/RBAC
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/me`
- `GET /api/v1/rbac/permissions`

### 6.2 Cases
- `POST /api/v1/cases`
- `GET /api/v1/cases`
- `GET /api/v1/cases/{case_id}`
- `PATCH /api/v1/cases/{case_id}`
- `POST /api/v1/cases/{case_id}/entities/bulk`

### 6.3 Enrichment/Analysis
- `POST /api/v1/enrichment/jobs`
- `GET /api/v1/enrichment/jobs/{job_id}`
- `GET /api/v1/observables/{id}/enrichments`
- `POST /api/v1/correlation/cluster`
- `GET /api/v1/campaigns/{campaign_id}`

### 6.4 Evidence
- `POST /api/v1/evidence/upload`
- `POST /api/v1/evidence/capture/url` (safe capture in isolated environment)
- `GET /api/v1/evidence/{id}`
- `POST /api/v1/evidence/{id}/seal`
- `GET /api/v1/evidence/{id}/chain`

### 6.5 Disruption/Reporting
- `POST /api/v1/abuse/complaints/generate`
- `POST /api/v1/abuse/complaints/submit` (manual review gate)
- `GET /api/v1/exports/ioc?format=csv|json|stix`
- `POST /api/v1/reports/generate`
- `GET /api/v1/reports/{report_id}/download`

### 6.6 Audit/Compliance
- `GET /api/v1/audit/logs`
- `POST /api/v1/legal-holds`
- `POST /api/v1/retention/apply`

---

## 7) Enrichment Pipeline

### 7.1 Pipeline Stages
1. **Normalize** indicator (canonical format, punycode, E.164 where applicable).
2. **Deduplicate** via content hash and value hash.
3. **Classify** entity type and risk context.
4. **Passive Enrich** (RDAP/WHOIS, DNS/PDNS, ASN, TLS cert metadata, reputation feeds).
5. **Contextual Correlate** (historical infra relation, kit/artifact similarity, wallet tags).
6. **Score** (confidence + risk + evidence quality).
7. **Persist** to Postgres + Neo4j.
8. **Queue actions** (analyst task, abuse-draft generation, IOC publication).

### 7.2 Job Semantics
- Idempotent jobs by `job_key`.
- Retry policy with dead-letter queue.
- Provider timeout budget and circuit breakers.
- Caching TTL by data source (e.g., RDAP 24h, DNS 1h).

---

## 8) Risk and Confidence Scoring

### 8.1 Confidence Score (0-100)
`confidence = source_reliability * evidence_quality * corroboration_factor * recency_factor`

Where:
- source_reliability: curated score per provider/source.
- evidence_quality: direct capture > third-party claim.
- corroboration_factor: multiple independent sources increase confidence.
- recency_factor: decays over time.

### 8.2 Risk Score (0-100)
Weighted model:
- indicator prevalence in known abuse sets (20%)
- campaign linkage strength (25%)
- victim impact potential (20%)
- active lure indicators (15%)
- infrastructure churn/evasion patterns (10%)
- internal telemetry hits (10%)

### 8.3 Explainability
Every score stores a feature contribution vector for analyst review.

---

## 9) Case Workflow (End-to-End)
1. Intake indicators and artifacts.
2. Auto-normalization and triage tagging.
3. Passive enrichment jobs run.
4. Graph correlation and campaign suggestion.
5. Analyst validates links and confidence.
6. Evidence sealing + chain-of-custody update.
7. Generate outputs:
   - executive summary,
   - researcher report,
   - LE referral package,
   - abuse complaints,
   - IOC feeds/STIX bundle.
8. Publish approved defensive actions to SIEM/EDR/firewall.
9. Retention clock starts unless legal hold active.

---

## 10) Repository Structure

```text
sentinelforge/
  backend/
    app/
      api/
      core/
      models/
      schemas/
      services/
      workers/
      connectors/
        base.py
        rdap/
        dns/
        reputation/
        abuse_platforms/
      reporting/
      compliance/
    tests/
  frontend/
    src/
      pages/
      components/
      hooks/
      api/
      store/
    tests/
  infra/
    docker/
    compose/
    migrations/
    neo4j/
    prometheus/
    grafana/
  data/
    demo/
      seed_cases.json
      seed_indicators.json
  docs/
    SOPs/
    legal/
    api/
```

---

## 11) UI Pages (React)
- Login/MFA
- Case Queue
- Case Detail (timeline + entities + evidence)
- Investigation Graph Explorer
- Observable Workbench (enrichment details)
- Evidence Vault (preview, hashes, chain entries)
- Abuse Action Center (draft and submit packages)
- IOC/STIX Export Center
- Compliance Admin (retention, legal hold, audit)
- Settings (connectors, API keys, tenant controls)

---

## 12) Sample JSON Objects

### 12.1 Case Object
```json
{
  "case_ref": "SF-2026-000184",
  "title": "Brand impersonation phishing cluster",
  "status": "in_review",
  "severity": "high",
  "entities": [
    {"type": "domain", "value": "secure-example-login.com"},
    {"type": "wallet", "value": "bc1qexample..."}
  ],
  "confidence": 82,
  "created_at": "2026-04-22T10:12:00Z"
}
```

### 12.2 Evidence Manifest
```json
{
  "evidence_id": "ev_4d8f",
  "kind": "web_capture",
  "sha256": "2ce7...ab9",
  "object_uri": "s3://evidence/case-SF-2026-000184/ev_4d8f.tar",
  "acquired_at": "2026-04-22T10:15:31Z",
  "chain": [
    {
      "event": "acquired",
      "actor": "analyst_17",
      "timestamp": "2026-04-22T10:15:31Z",
      "record_hash": "6b9..."
    }
  ]
}
```

---

## 13) Sample STIX 2.1 Bundle
```json
{
  "type": "bundle",
  "id": "bundle--02d7a4a8-9dd7-4fca-95c6-6ef4f127ef31",
  "objects": [
    {
      "type": "indicator",
      "spec_version": "2.1",
      "id": "indicator--d96dca1a-fb3e-40f3-ae2c-2ce3aa80fb2b",
      "created": "2026-04-22T10:30:00.000Z",
      "modified": "2026-04-22T10:30:00.000Z",
      "name": "Phishing domain",
      "pattern": "[domain-name:value = 'secure-example-login.com']",
      "pattern_type": "stix",
      "valid_from": "2026-04-22T10:30:00.000Z",
      "labels": ["phishing", "credential-harvest-theme"]
    },
    {
      "type": "relationship",
      "spec_version": "2.1",
      "id": "relationship--fb6994ca-76ba-47d8-b0d0-35fa63cde769",
      "relationship_type": "indicates",
      "source_ref": "indicator--d96dca1a-fb3e-40f3-ae2c-2ce3aa80fb2b",
      "target_ref": "campaign--3ae4f7d4-8ad7-4ea7-b4fd-2f2d5e3d59c3",
      "created": "2026-04-22T10:30:00.000Z",
      "modified": "2026-04-22T10:30:00.000Z"
    }
  ]
}
```

---

## 14) Sample Report Templates

### 14.1 Executive Summary (1-2 pages)
- Incident/case overview
- Business impact
- Confidence statement
- Recommended immediate controls
- Status of provider/registrar reports

### 14.2 Technical Research Report
- Full IOC list with provenance
- Infra relationship graph snapshots
- Capture artifacts and hashes
- Cluster rationale and scoring breakdown

### 14.3 LE Referral Package
- Case narrative with UTC timestamps
- Evidence manifest and chain-of-custody records
- Jurisdiction notes and legal process references
- Contact matrix and escalation log

---

## 15) Deployment (Docker Compose)

### 15.1 Services
- `frontend` (React)
- `backend` (FastAPI + gunicorn/uvicorn)
- `worker` (Celery)
- `postgres`
- `neo4j`
- `redis`
- `minio`
- `prometheus`, `grafana`, `loki`
- `nginx` reverse proxy with TLS termination

### 15.2 Steps
1. Copy `.env.example` to `.env` and set secrets.
2. Initialize databases and run migrations.
3. Bootstrap admin account with MFA.
4. Enable connectors with API keys.
5. Import demo dataset.
6. Run smoke tests and health checks.
7. Configure backups (Postgres WAL + object storage versioning).
8. Enable centralized logging and alerts.

### 15.3 HA/Resilience
- Postgres replication or managed HA.
- Redis persistence + sentinel (or managed equivalent).
- Daily restore tests.
- Immutable evidence bucket policy with retention lock.

---

## 16) SOPs (Operational)

1. **Indicator Intake SOP**: validation, triage class, legal basis tagging.
2. **Safe Capture SOP**: isolated browser workflow, malware-safe handling, checksum verification.
3. **Evidence Integrity SOP**: hashing, sealing, chain updates, legal hold checks.
4. **Abuse Reporting SOP**: review gate, approved templates, follow-up cadence.
5. **Defensive Blocklist SOP**: test mode, staged rollout, rollback plan.
6. **LE Referral SOP**: package checklist, approved counsel review, secure transfer.
7. **Analyst OPSEC SOP**: separate identities, hardened workstations, no personal account cross-use.

---

## 17) Legal/Ethical Boundaries (Non-negotiable Guardrails)
- Collect/process only lawfully obtained data and authorized telemetry.
- No unauthorized access attempts, intrusion, persistence, or active compromise.
- No precise live-location tracking of individuals.
- PII minimization and strict purpose limitation.
- Jurisdiction-aware processing with data residency controls.
- Human approval required for external submissions and disruption actions.
- Full auditability for every analyst and system action.

---

## 18) Testing Strategy
- **Unit tests**: parsers, normalizers, score calculators.
- **Integration tests**: connector outputs, API authz, evidence lifecycle.
- **Contract tests**: plugin interface compatibility.
- **E2E tests**: case intake → enrichment → report generation.
- **Security tests**: SAST, dependency scan, container scan, RBAC tests.
- **Chaos tests**: provider timeout, queue backlog, DB failover.

Target coverage:
- Backend: 85%+
- Frontend critical flows: 70%+

---

## 19) Demo Dataset (Seed)
Include sanitized examples:
- 20 domains, 35 URLs, 18 IPs, 12 wallets, 40 screenshots metadata, 8 phishing emails (headers only), 5 sandbox summaries.
- Pre-linked 3 campaigns with varying confidence levels.

---

## 20) Implementation Roadmap (90 Days)
- **Phase 1 (Weeks 1-3):** core schema, auth/RBAC, case intake, basic enrichment.
- **Phase 2 (Weeks 4-6):** evidence pipeline, chain-of-custody, graph correlation MVP.
- **Phase 3 (Weeks 7-9):** reporting engine, STIX/TAXII export, abuse action center.
- **Phase 4 (Weeks 10-12):** hardening, observability, SOP rollout, pilot operations.

---

## 21) Minimal Plugin Interface (Python)
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class Connector(ABC):
    name: str
    version: str

    @abstractmethod
    async def enrich(self, observable: Dict[str, Any]) -> Dict[str, Any]:
        """Return parsed enrichment and provenance metadata."""

    @abstractmethod
    def healthcheck(self) -> Dict[str, Any]:
        """Return status and dependency checks."""
```

---

## 22) Additional Recommendations (Missing but Important)
- Add policy-as-code guardrails (OPA) for disruption actions.
- Add adversarial data poisoning detection in ingestion.
- Add duplicate-case recommendation engine.
- Support multi-tenant segregation with per-tenant KMS keys.
- Build legal request tracker for subpoenas/production requests.

