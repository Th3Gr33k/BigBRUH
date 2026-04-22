from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.case import Case, CaseEntity

router = APIRouter(prefix='/exports', tags=['exports'])


@router.get('/ioc')
def export_ioc(format: str = Query('json', pattern='^(json|csv)$'), case_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(CaseEntity)
    if case_id is not None:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail='case not found')
        query = query.filter(CaseEntity.case_id == case_id)

    rows = query.all()
    if format == 'json':
        return {'items': [{'type': r.entity_type, 'value': r.entity_value, 'case_id': r.case_id} for r in rows]}

    csv_lines = ['case_id,type,value']
    csv_lines.extend([f'{r.case_id},{r.entity_type},{r.entity_value}' for r in rows])
    return {'csv': '\n'.join(csv_lines)}
