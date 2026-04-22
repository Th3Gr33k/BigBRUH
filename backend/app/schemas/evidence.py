from datetime import datetime

from pydantic import BaseModel


class EvidenceCreate(BaseModel):
    case_id: int
    kind: str
    content: str
    object_uri: str


class EvidenceOut(BaseModel):
    id: int
    case_id: int
    kind: str
    sha256: str
    object_uri: str
    created_at: datetime

    model_config = {'from_attributes': True}
