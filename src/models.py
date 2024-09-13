from datetime import timezone
from enum import Enum
from pydantic import BaseModel, Field

class TenderStatus(str, Enum):
    CREATED = "Created"
    PUBLISHED = "Published"
    CLOSED = "Closed"

class TenderServiceType(str, Enum):
    CONSTRUCTION = "Construction"
    DELIVERY = "Delivery"
    MANUFACTURE = "Manufacture"

class TenderCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    serviceType: TenderServiceType
    organizationId: str = Field(..., max_length=100)
    creatorUsername: str

class TenderUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)
    serviceType: TenderServiceType | None = None

class TenderOut(BaseModel):
    id: str = Field(..., max_length=100)
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    serviceType: TenderServiceType
    status: TenderStatus
    organizationId: str = Field(..., max_length=100)
    version: int = Field(..., ge=1)
    createdAt: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            name=obj.name,
            description=obj.description,
            serviceType=obj.service_type.value,
            status=obj.status.value,
            organizationId=str(obj.organization_id),
            version=obj.version,
            createdAt=cls.format_rfc3339(obj.created_at)
            )

    @staticmethod
    def format_rfc3339(dt):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")

class PaginationParameters(BaseModel):
    limit: int = Field(5, ge=0, le=50)
    offset: int = Field(0, ge=0)

class ErrorResponse(BaseModel):
    reason: str = Field(..., min_length=5)

class TenderStatusResponse(BaseModel):
    status: TenderStatus

    class Config:
        orm_mode = True
