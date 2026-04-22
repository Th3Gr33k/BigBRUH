import hashlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.case import Case
from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceCreate, EvidenceOut

router = APIRouter(prefix='/evidence', tags=['evidence'])


@router.post('', response_model=EvidenceOut)
def create_evidence(payload: EvidenceCreate, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == payload.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail='case not found')

    sha256 = hashlib.sha256(payload.content.encode('utf-8')).hexdigest()
    evidence = Evidence(case_id=payload.case_id, kind=payload.kind, sha256=sha256, object_uri=payload.object_uri)
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


@router.get('/{evidence_id}', response_model=EvidenceOut)
def get_evidence(evidence_id: int, db: Session = Depends(get_db)):
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail='evidence not found')
    return evidence
