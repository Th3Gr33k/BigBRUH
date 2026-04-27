from datetime import datetime

from pydantic import BaseModel


class CaseCreate(BaseModel):
    case_ref: str
    title: str
    severity: str = 'medium'


class CaseEntityIn(BaseModel):
    entity_type: str
    entity_value: str


class CaseEntityOut(CaseEntityIn):
    id: int

    model_config = {'from_attributes': True}


class CaseOut(BaseModel):
    id: int
    case_ref: str
    title: str
    status: str
    severity: str
    created_at: datetime
    entities: list[CaseEntityOut] = []

    model_config = {'from_attributes': True}
