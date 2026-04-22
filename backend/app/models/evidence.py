from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Evidence(Base):
    __tablename__ = 'evidence_items'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey('cases.id', ondelete='RESTRICT'))
    kind: Mapped[str] = mapped_column(String(64))
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    object_uri: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
