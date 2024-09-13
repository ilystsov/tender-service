from sqlalchemy import select, update
from sqlalchemy.orm import Session
from uuid import UUID
from src.db.models import Tender, User, TenderHistory, Organization, TenderServiceType, OrganizationResponsible, TenderStatus
from src.exceptions import TenderNotFound, UserNotFound, PermissionDenied, TenderVersionNotFound, OrganizationNotFound
from src.db.schemas import TenderCreate, TenderUpdate


def is_user_responsible_for_organization(db: Session, user_id: UUID, organization_id: UUID) -> bool:
    query = select(OrganizationResponsible).where(
        OrganizationResponsible.user_id == user_id,
        OrganizationResponsible.organization_id == organization_id
    )
    result = db.execute(query).scalar_one_or_none()
    return result is not None


def get_user_by_username(db: Session, username: str) -> User:
    query = select(User).where(User.username == username)
    user = db.execute(query).scalar_one_or_none()
    if not user:
        raise UserNotFound(f"User with username '{username}' not found")
    return user


def get_tenders(db: Session, service_type: list[TenderServiceType] | None = None, limit: int = 5, offset: int = 0) -> list[Tender]:
    query = select(Tender).where(Tender.status == TenderStatus.PUBLISHED).limit(limit).offset(offset).order_by(Tender.name)
    if service_type:
        service_type_values = [st.value.upper() for st in service_type]
        query = query.where(Tender.service_type.in_(service_type_values))
    return db.scalars(query).all()



def get_tender_by_id(db: Session, tender_id: UUID) -> Tender:
    tender = db.get(Tender, tender_id)
    if tender is None:
        raise TenderNotFound(f"Tender with id {tender_id} not found.")
    return tender


def create_tender(db: Session, tender_data: TenderCreate) -> Tender:
    user = get_user_by_username(db, tender_data.creatorUsername)

    organization = db.get(Organization, tender_data.organizationId)
    if not organization:
        raise OrganizationNotFound(f"Organization with id '{tender_data.organizationId}' not found")

    if not is_user_responsible_for_organization(db, user.id, tender_data.organizationId):
        raise PermissionDenied(f"User '{tender_data.creatorUsername}' does not have permission to create tender for this organization")

    tender = Tender(
        name=tender_data.name,
        description=tender_data.description,
        service_type=tender_data.serviceType.value.upper(),
        organization_id=tender_data.organizationId,
        status=TenderStatus.CREATED
    )
    db.add(tender)
    db.commit()
    db.refresh(tender)
    return tender


def get_tenders_by_user(db: Session, username: str, limit: int = 5, offset: int = 0) -> list[Tender]:
    user = get_user_by_username(db, username)

    query = select(Tender).join(Tender.organization).join(OrganizationResponsible).where(
        OrganizationResponsible.user_id == user.id
    )
    return db.scalars(query.limit(limit).offset(offset).order_by(Tender.name)).all()



def get_tender_status(db: Session, tender_id: UUID, username: str) -> TenderStatus:
    user = get_user_by_username(db, username)
    tender = get_tender_by_id(db, tender_id)
    if tender.status != TenderStatus.PUBLISHED:
        if not is_user_responsible_for_organization(db, user.id, tender.organization_id):
            raise PermissionDenied(f"User '{username}' does not have permission to view the status of this tender")
    return tender.status

def save_tender_history(db: Session, tender: Tender):
    history = TenderHistory(
        tender_id=tender.id,
        name=tender.name,
        description=tender.description,
        service_type=tender.service_type,
        status=tender.status,
        version=tender.version
    )
    db.add(history)
    db.commit()


def update_tender(db: Session, tender_id: UUID, tender_data: TenderUpdate, username: str) -> Tender:
    user = get_user_by_username(db, username)
    tender = get_tender_by_id(db, tender_id)

    if not is_user_responsible_for_organization(db, user.id, tender.organization_id):
        raise PermissionDenied(f"User '{username}' does not have permission to update this tender")

    update_values = {}
    if tender_data.name is not None:
        update_values["name"] = tender_data.name
    if tender_data.description is not None:
        update_values["description"] = tender_data.description
    if tender_data.serviceType is not None:
        update_values["service_type"] = tender_data.serviceType.value.upper()

    if update_values:
        update_values["version"] = tender.version + 1

        save_tender_history(db, tender)
        query = update(Tender).where(Tender.id == tender_id).values(update_values).execution_options(
            synchronize_session="fetch")
        db.execute(query)
        db.commit()
        db.refresh(tender)

    return tender


def update_tender_status(db: Session, tender_id: UUID, new_status: TenderStatus, username: str) -> Tender:
    user = get_user_by_username(db, username)
    tender = get_tender_by_id(db, tender_id)

    if not is_user_responsible_for_organization(db, user.id, tender.organization_id):
        raise PermissionDenied(f"User '{username}' does not have permission to update the status of this tender")

    save_tender_history(db, tender)
    query = update(Tender).where(Tender.id == tender_id).values(
        status=new_status.value.upper(),
        version=tender.version + 1
    ).execution_options(synchronize_session="fetch")
    db.execute(query)
    db.commit()
    db.refresh(tender)

    return tender


def rollback_tender_version(db: Session, tender_id: UUID, version: int, username: str) -> Tender:
    user = get_user_by_username(db, username)
    tender = get_tender_by_id(db, tender_id)

    if not is_user_responsible_for_organization(db, user.id, tender.organization_id):
        raise PermissionDenied(f"User '{username}' does not have permission to rollback this tender")

    query = select(TenderHistory).where(
        TenderHistory.tender_id == tender_id,
        TenderHistory.version == version
    )
    history_record = db.execute(query).scalar_one_or_none()

    if not history_record:
        raise TenderVersionNotFound(f"Tender version '{version}' not found for tender ID '{tender_id}'")

    save_tender_history(db, tender)
    query = update(Tender).where(Tender.id == tender_id).values(
        name=history_record.name,
        description=history_record.description,
        service_type=history_record.service_type,
        status=history_record.status,
        version=tender.version + 1
    ).execution_options(synchronize_session="fetch")
    db.execute(query)
    db.commit()
    db.refresh(tender)
    return tender
