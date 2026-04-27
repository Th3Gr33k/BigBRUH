from datetime import datetime

from pydantic import BaseModel


class EnrichmentJobRequest(BaseModel):
    observable_type: str
    value: str


class EnrichmentResult(BaseModel):
    observable_type: str
    value: str
    normalized: str
    confidence: int
    notes: list[str]


class EnrichmentJobOut(BaseModel):
    job_id: str
    status: str
    created_at: datetime | None = None
    result: EnrichmentResult | None = None
