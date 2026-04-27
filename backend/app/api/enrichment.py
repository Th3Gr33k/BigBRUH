import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_api_key
from app.models.enrichment import EnrichmentJob
from app.schemas.enrichment import EnrichmentJobRequest, EnrichmentJobOut, EnrichmentResult
from app.services.enrichment import create_job

router = APIRouter(prefix='/enrichment', tags=['enrichment'])


@router.post('/jobs', response_model=EnrichmentJobOut)
def create_enrichment_job(payload: EnrichmentJobRequest, actor: str = Depends(require_api_key), db: Session = Depends(get_db)):
    del actor
    try:
        job = create_job(db, payload.observable_type, payload.value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    result = EnrichmentResult(**json.loads(job.result_json))
    return EnrichmentJobOut(job_id=job.job_id, status='queued', created_at=job.created_at, result=result)


@router.get('/jobs/{job_id}', response_model=EnrichmentJobOut)
def get_job(job_id: str, actor: str = Depends(require_api_key), db: Session = Depends(get_db)):
    del actor
    job = db.query(EnrichmentJob).filter(EnrichmentJob.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail='job not found')
    result = EnrichmentResult(**json.loads(job.result_json))
    return EnrichmentJobOut(job_id=job.job_id, status=job.status, created_at=job.created_at, result=result)
