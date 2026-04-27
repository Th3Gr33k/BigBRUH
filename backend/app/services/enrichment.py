import json
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.enrichment import EnrichmentJob
from app.schemas.enrichment import EnrichmentResult


ALLOWED_TYPES = {'domain', 'url', 'ip', 'email', 'phone', 'wallet'}


def normalize_value(observable_type: str, value: str) -> str:
    normalized = value.strip().lower()
    if observable_type in {'domain', 'url'}:
        normalized = normalized.removeprefix('http://').removeprefix('https://').rstrip('/')
    return normalized


def enrich_passive(observable_type: str, value: str) -> EnrichmentResult:
    normalized = normalize_value(observable_type, value)
    notes = [
        'Passive enrichment only',
        'No active exploitation or unauthorized access',
        f'Observable type: {observable_type}',
    ]
    confidence = 55 if observable_type in {'domain', 'ip', 'url'} else 45
    return EnrichmentResult(
        observable_type=observable_type,
        value=value,
        normalized=normalized,
        confidence=confidence,
        notes=notes,
    )


def create_job(db: Session, observable_type: str, value: str) -> EnrichmentJob:
    if observable_type not in ALLOWED_TYPES:
        raise ValueError(f'unsupported observable_type: {observable_type}')
    result = enrich_passive(observable_type, value)
    job = EnrichmentJob(
        job_id=str(uuid4()),
        observable_type=observable_type,
        observable_value=value,
        status='completed',
        result_json=json.dumps(result.model_dump()),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
