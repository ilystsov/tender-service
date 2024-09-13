from sqlalchemy import ForeignKey, String, Enum, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
from src.db.database import BaseModel
import enum


class OrganizationType(enum.Enum):
    IE = "IE"
    LLC = "LLC"
    JSC = "JSC"


class OrganizationResponsible(BaseModel):
    __tablename__ = "organization_responsible"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organization.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("employee.id", ondelete="CASCADE"))

    organization: Mapped["Organization"] = relationship("Organization", back_populates="responsibles")
    user: Mapped["User"] = relationship("User", back_populates="organizations")



class User(BaseModel):
    __tablename__ = "employee"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    organizations: Mapped[list["OrganizationResponsible"]] = relationship("OrganizationResponsible", back_populates="user")

class Organization(BaseModel):
    __tablename__ = "organization"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    type: Mapped[OrganizationType] = mapped_column(Enum(OrganizationType), nullable=True)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    responsibles: Mapped[list["OrganizationResponsible"]] = relationship("OrganizationResponsible", back_populates="organization")
    tenders: Mapped[list["Tender"]] = relationship("Tender", back_populates="organization")


class TenderStatus(enum.Enum):
    CREATED = "Created"
    PUBLISHED = "Published"
    CLOSED = "Closed"


class TenderServiceType(enum.Enum):
    CONSTRUCTION = "Construction"
    DELIVERY = "Delivery"
    MANUFACTURE = "Manufacture"


class TenderHistory(BaseModel):
    __tablename__ = "tender_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tender.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    service_type: Mapped[TenderServiceType] = mapped_column(Enum(TenderServiceType), nullable=False)
    status: Mapped[TenderStatus] = mapped_column(Enum(TenderStatus), nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)

    tender: Mapped["Tender"] = relationship("Tender", back_populates="history")


class Tender(BaseModel):
    __tablename__ = "tender"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    service_type: Mapped[TenderServiceType] = mapped_column(Enum(TenderServiceType), nullable=False)
    status: Mapped[TenderStatus] = mapped_column(Enum(TenderStatus), nullable=False, default=TenderStatus.CREATED)
    version: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organization.id", ondelete="CASCADE"), nullable=False)
    organization: Mapped["Organization"] = relationship("Organization", back_populates="tenders")

    bids: Mapped[list["Bid"]] = relationship("Bid", back_populates="tender", cascade="all, delete-orphan")
    history: Mapped[list["TenderHistory"]] = relationship("TenderHistory", back_populates="tender", cascade="all, delete-orphan")

class BidStatus(enum.Enum):
    CREATED = "Created"
    PUBLISHED = "Published"
    CANCELED = "Canceled"


class AuthorType(enum.Enum):
    USER = "User"
    ORGANIZATION = "Organization"


class Bid(BaseModel):
    __tablename__ = "bid"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[BidStatus] = mapped_column(Enum(BidStatus), nullable=False, default=BidStatus.CREATED)
    version: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    tender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tender.id", ondelete="CASCADE"), nullable=False)
    tender: Mapped["Tender"] = relationship("Tender", back_populates="bids")

    author_type: Mapped[AuthorType] = mapped_column(Enum(AuthorType), nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(nullable=False)

