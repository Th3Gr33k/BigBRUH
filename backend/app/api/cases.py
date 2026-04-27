from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_api_key
from app.models.case import Case, CaseEntity
from app.schemas.case import CaseCreate, CaseEntityIn, CaseOut

router = APIRouter(prefix='/cases', tags=['cases'])


@router.post('', response_model=CaseOut)
def create_case(payload: CaseCreate, actor: str = Depends(require_api_key), db: Session = Depends(get_db)):
    del actor
    exists = db.query(Case).filter(Case.case_ref == payload.case_ref).first()
    if exists:
        raise HTTPException(status_code=409, detail='case_ref already exists')
    case = Case(case_ref=payload.case_ref, title=payload.title, severity=payload.severity)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get('', response_model=list[CaseOut])
def list_cases(actor: str = Depends(require_api_key), db: Session = Depends(get_db)):
    del actor
    return db.query(Case).order_by(Case.id.desc()).all()


@router.get('/{case_id}', response_model=CaseOut)
def get_case(case_id: int, actor: str = Depends(require_api_key), db: Session = Depends(get_db)):
    del actor
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail='case not found')
    return case


@router.post('/{case_id}/entities/bulk', response_model=CaseOut)
def add_entities(case_id: int, entities: list[CaseEntityIn], actor: str = Depends(require_api_key), db: Session = Depends(get_db)):
    del actor
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail='case not found')
    for item in entities:
        db.add(CaseEntity(case_id=case_id, entity_type=item.entity_type, entity_value=item.entity_value))
    db.commit()
    db.refresh(case)
    return case
