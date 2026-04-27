from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Case(Base):
    __tablename__ = 'cases'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_ref: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default='new')
    severity: Mapped[str] = mapped_column(String(16), default='medium')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    entities: Mapped[list['CaseEntity']] = relationship(back_populates='case', cascade='all, delete-orphan')


class CaseEntity(Base):
    __tablename__ = 'case_entities'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey('cases.id', ondelete='CASCADE'))
    entity_type: Mapped[str] = mapped_column(String(32), index=True)
    entity_value: Mapped[str] = mapped_column(Text)

    case: Mapped[Case] = relationship(back_populates='entities')
