from fastapi import APIRouter, Depends
from redis import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db

router = APIRouter(tags=['health'])


@router.get('/healthz')
def healthz():
    return {'status': 'ok'}


@router.get('/readyz')
def readyz(db: Session = Depends(get_db)):
    checks = {'database': False, 'redis': False, 'neo4j_configured': False}

    try:
        db.execute(text('SELECT 1'))
        checks['database'] = True
    except Exception:
        checks['database'] = False

    try:
        redis = Redis.from_url(settings.redis_url)
        checks['redis'] = bool(redis.ping())
    except Exception:
        checks['redis'] = False

    checks['neo4j_configured'] = bool(settings.neo4j_uri and settings.neo4j_user)

    overall = all(checks.values())
    return {'status': 'ready' if overall else 'degraded', 'checks': checks}
