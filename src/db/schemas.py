from pydantic import BaseModel
from uuid import UUID

from src.db.models import TenderServiceType, AuthorType


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


class BidCreate(BaseModel):
    name: str
    description: str
    tenderId: UUID
    authorType: AuthorType
    authorId: UUID

class BidUpdate(BaseModel):
    name: str | None = None
    description: str | None = None