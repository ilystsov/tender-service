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


class TenderStatusResponse(BaseModel):
    status: TenderStatus

    class Config:
        orm_mode = True



class BidStatus(str, Enum):
    CREATED = "Created"
    PUBLISHED = "Published"
    CANCELED = "Canceled"

class AuthorType(str, Enum):
    USER = "User"
    ORGANIZATION = "Organization"

class BidCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    tenderId: str = Field(..., max_length=100)
    authorType: AuthorType
    authorId: str = Field(..., max_length=100)

class BidUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)

class BidOut(BaseModel):
    id: str = Field(..., max_length=100)
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    status: BidStatus
    tenderId: str = Field(..., max_length=100)
    authorType: AuthorType
    authorId: str = Field(..., max_length=100)
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
            status=obj.status.value,
            tenderId=str(obj.tender_id),
            authorType=obj.author_type.value,
            authorId=str(obj.author_id),
            version=obj.version,
            createdAt=cls.format_rfc3339(obj.created_at)
        )

    @staticmethod
    def format_rfc3339(dt):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")


class BidFeedbackOut(BaseModel):
    id: str = Field(..., max_length=100)
    description: str = Field(..., max_length=1000)
    createdAt: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=str(obj.id),
            description=obj.feedback,
            createdAt=cls.format_rfc3339(obj.created_at)
        )

    @staticmethod
    def format_rfc3339(dt):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace("+00:00", "Z")