from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_api_key
from app.models.audit import AuditLog

router = APIRouter(prefix='/audit', tags=['audit'])


@router.get('/logs')
def list_audit_logs(limit: int = 100, actor: str = Depends(require_api_key), db: Session = Depends(get_db)):
    del actor
    limit = min(max(limit, 1), 1000)
    rows = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    return {
        'items': [
            {
                'request_id': r.request_id,
                'method': r.method,
                'path': r.path,
                'status_code': r.status_code,
                'actor': r.actor,
                'detail': r.detail,
                'created_at': r.created_at.isoformat(),
            }
            for r in rows
        ]
    }
