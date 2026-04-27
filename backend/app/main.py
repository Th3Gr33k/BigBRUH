import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.audit import router as audit_router
from app.api.cases import router as cases_router
from app.api.enrichment import router as enrichment_router
from app.api.evidence import router as evidence_router
from app.api.exports import router as exports_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.db import Base, SessionLocal, engine
from app.models.audit import AuditLog

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)

origins = [o.strip() for o in settings.allowed_origins.split(',') if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def audit_middleware(request: Request, call_next):
    request_id = request.headers.get('x-request-id', str(uuid4()))
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    response.headers['x-request-id'] = request_id

    db = SessionLocal()
    try:
        db.add(
            AuditLog(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                actor=request.headers.get('x-actor', 'system'),
                detail=f'elapsed_ms={elapsed_ms}',
            )
        )
        db.commit()
    finally:
        db.close()

    logger.info('%s %s %s %sms', request.method, request.url.path, response.status_code, elapsed_ms)
    return response


@app.on_event('startup')
def on_startup():
    Base.metadata.create_all(bind=engine)
    logger.info('SentinelForge API started in %s mode', settings.environment)


app.include_router(health_router)
app.include_router(cases_router, prefix=settings.api_prefix)
app.include_router(enrichment_router, prefix=settings.api_prefix)
app.include_router(evidence_router, prefix=settings.api_prefix)
app.include_router(exports_router, prefix=settings.api_prefix)
app.include_router(audit_router, prefix=settings.api_prefix)
