from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class EnrichmentJob(Base):
    __tablename__ = 'enrichment_jobs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    observable_type: Mapped[str] = mapped_column(String(32))
    observable_value: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default='queued')
    result_json: Mapped[str] = mapped_column(Text, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
