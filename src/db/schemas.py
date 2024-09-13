from pydantic import BaseModel
from uuid import UUID

from src.db.models import TenderServiceType


class TenderCreate(BaseModel):
    name: str
    description: str
    serviceType: TenderServiceType
    organizationId: UUID
    creatorUsername: str


class TenderUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    serviceType: TenderServiceType | None = None


