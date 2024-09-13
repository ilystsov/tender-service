
from sqlalchemy import select, update, or_, and_
from sqlalchemy.orm import Session
from uuid import UUID
from src.db.models import Tender, User, TenderHistory, Organization, TenderServiceType, OrganizationResponsible, \
    TenderStatus, Bid, BidStatus, BidHistory, AuthorType, BidDecisionStatus, BidDecision, BidFeedback
from src.exceptions import TenderNotFound, UserNotFound, PermissionDenied, TenderVersionNotFound, OrganizationNotFound, \
    BidNotFound, BidVersionNotFound
from src.db.schemas import TenderCreate, TenderUpdate, BidCreate, BidUpdate


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





def create_bid(db: Session, bid_data: BidCreate) -> Bid:
    user = db.get(User, bid_data.authorId)
    tender = db.get(Tender, bid_data.tenderId)

    if tender is None:
        raise TenderNotFound(f"Tender with id {bid_data.tenderId} not found")

    if bid_data.authorType == AuthorType.ORGANIZATION.value:
        responsible_for_any_org = db.query(OrganizationResponsible).filter_by(user_id=user.id).first()
        if responsible_for_any_org is None:
            raise PermissionDenied(f"User '{user.username}' does not have permission to create bids from an organization")

    bid = Bid(
        name=bid_data.name,
        description=bid_data.description,
        tender_id=bid_data.tenderId,
        status=BidStatus.CREATED,
        author_type=bid_data.authorType.value.upper(),
        author_id=bid_data.authorId,
    )
    db.add(bid)
    db.commit()
    db.refresh(bid)
    return bid



def get_bids_by_user(db: Session, username: str, limit: int = 5, offset: int = 0) -> list[Bid]:
    user = get_user_by_username(db, username)

    responsible_orgs_query = select(OrganizationResponsible.organization_id).where(
        OrganizationResponsible.user_id == user.id
    )
    responsible_orgs = db.scalars(responsible_orgs_query).all()

    query = select(Bid).where(
        or_(
            Bid.author_id == user.id,
            and_(Bid.author_type == AuthorType.ORGANIZATION, Bid.author_id.in_(responsible_orgs))  # Ответственный за организацию предложения
        )
    ).limit(limit).offset(offset).order_by(Bid.name)

    return db.scalars(query).all()


def get_bids_for_tender(db: Session, tender_id: UUID, username: str, limit: int = 5, offset: int = 0) -> list[Bid]:
    user = get_user_by_username(db, username)
    tender = db.get(Tender, tender_id)

    if not tender:
        raise TenderNotFound(f"Tender with id {tender_id} not found")

    is_responsible = is_user_responsible_for_organization(db, user.id, tender.organization_id)
    query = select(Bid).where(
        Bid.tender_id == tender_id
    ).where(
        or_(
            Bid.status == BidStatus.PUBLISHED,
            Bid.author_id == user.id,
            is_responsible
        )
    ).limit(limit).offset(offset).order_by(Bid.name)

    return db.scalars(query).all()


def get_bid_status(db: Session, bid_id: UUID, username: str) -> BidStatus:
    user = get_user_by_username(db, username)
    bid = db.get(Bid, bid_id)

    if not bid:
        raise BidNotFound(f"Bid with id {bid_id} not found")

    is_responsible = is_user_responsible_for_organization(db, user.id, bid.tender.organization_id)

    if bid.status == BidStatus.PUBLISHED or bid.author_id == user.id or is_responsible:
        return bid.status
    else:
        raise PermissionDenied(f"User '{username}' does not have permission to view the status of this bid")



def save_bid_history(db: Session, bid: Bid):
    history = BidHistory(
        bid_id=bid.id,
        name=bid.name,
        description=bid.description,
        status=bid.status,
        version=bid.version
    )
    db.add(history)
    db.commit()


def update_bid(db: Session, bid_id: UUID, bid_data: BidUpdate, username: str) -> Bid:
    user = get_user_by_username(db, username)
    bid = db.get(Bid, bid_id)

    if not bid:
        raise BidNotFound(f"Bid with id {bid_id} not found")

    is_responsible = is_user_responsible_for_organization(db, user.id, bid.tender.organization_id)

    if bid.author_id != user.id and not is_responsible:
        raise PermissionDenied(f"User '{username}' does not have permission to update this bid")

    update_values = {}
    if bid_data.name is not None:
        update_values["name"] = bid_data.name
    if bid_data.description is not None:
        update_values["description"] = bid_data.description

    if update_values:
        save_bid_history(db, bid)
        update_values["version"] = bid.version + 1

        query = update(Bid).where(Bid.id == bid_id).values(update_values).execution_options(synchronize_session="fetch")
        db.execute(query)
        db.commit()
        db.refresh(bid)

    return bid



def update_bid_status(db: Session, bid_id: UUID, new_status: BidStatus, username: str) -> Bid:
    user = get_user_by_username(db, username)
    bid = db.get(Bid, bid_id)

    if not bid:
        raise BidNotFound(f"Bid with id {bid_id} not found")

    is_responsible = is_user_responsible_for_organization(db, user.id, bid.tender.organization_id)

    if bid.author_id != user.id and not is_responsible:
        raise PermissionDenied(f"User '{username}' does not have permission to update the status of this bid")

    save_bid_history(db, bid)

    query = update(Bid).where(Bid.id == bid_id).values(
        status=new_status.value.upper(),
        version=bid.version + 1
    ).execution_options(synchronize_session="fetch")
    db.execute(query)
    db.commit()
    db.refresh(bid)

    return bid



def rollback_bid_version(db: Session, bid_id: UUID, version: int, username: str) -> Bid:
    user = get_user_by_username(db, username)
    bid = db.get(Bid, bid_id)

    if not bid:
        raise BidNotFound(f"Bid with id {bid_id} not found")

    is_responsible = is_user_responsible_for_organization(db, user.id, bid.tender.organization_id)

    if bid.author_id != user.id and not is_responsible:
        raise PermissionDenied(f"User '{username}' does not have permission to rollback this bid")

    query = select(BidHistory).where(
        BidHistory.bid_id == bid_id,
        BidHistory.version == version
    )
    history_record = db.execute(query).scalar_one_or_none()

    if not history_record:
        raise BidVersionNotFound(f"Bid version '{version}' not found for bid ID '{bid_id}'")

    save_bid_history(db, bid)

    # Откат предложения к указанной версии и инкремент новой версии
    query = update(Bid).where(Bid.id == bid_id).values(
        name=history_record.name,
        description=history_record.description,
        status=history_record.status,
        version=bid.version + 1
    ).execution_options(synchronize_session="fetch")
    db.execute(query)
    db.commit()
    db.refresh(bid)

    return bid


def submit_bid_decision(db: Session, bid_id: UUID, decision: BidDecisionStatus, username: str) -> Bid:
    user = get_user_by_username(db, username)
    bid = db.get(Bid, bid_id)

    if not bid:
        raise BidNotFound(f"Bid with id {bid_id} not found")

    if not is_user_responsible_for_organization(db, user.id, bid.tender.organization_id):
        raise PermissionDenied(f"User '{username}' does not have permission to make decisions on this bid")

    bid_decision = BidDecision(
        bid_id=bid.id,
        user_id=user.id,
        decision=decision
    )
    db.add(bid_decision)
    db.commit()

    rejected_decision = db.scalars(
        select(BidDecision).where(BidDecision.bid_id == bid.id, BidDecision.decision == BidDecisionStatus.REJECTED)
    ).one_or_none()

    if rejected_decision:
        bid.status = BidStatus.CANCELED
        db.commit()
        return bid

    responsible_count = db.scalars(
        select(OrganizationResponsible).where(OrganizationResponsible.organization_id == bid.tender.organization_id)
    ).count()

    quorum = min(3, responsible_count)
    approved_count = db.scalars(
        select(BidDecision).where(BidDecision.bid_id == bid.id, BidDecision.decision == BidDecisionStatus.APPROVED)
    ).count()

    if approved_count >= quorum:
        bid.tender.status = TenderStatus.CLOSED
        db.commit()

    return bid


def submit_bid_feedback(db: Session, bid_id: UUID, feedback_text: str, username: str) -> Bid:
    user = get_user_by_username(db, username)

    bid = db.get(Bid, bid_id)
    if not bid:
        raise BidNotFound(f"Bid with id {bid_id} not found")

    if not is_user_responsible_for_organization(db, user.id, bid.tender.organization_id):
        raise PermissionDenied(f"User '{username}' does not have permission to submit feedback on this bid")

    feedback = BidFeedback(
        bid_id=bid.id,
        user_id=user.id,
        feedback=feedback_text
    )
    db.add(feedback)
    db.commit()

    db.refresh(bid)
    return bid


def get_bid_feedbacks(db: Session, tender_id: UUID, author_username: str, requester_username: str, limit: int = 5,
                      offset: int = 0) -> list[BidFeedback]:
    requester = get_user_by_username(db, requester_username)
    author = get_user_by_username(db, author_username)

    tender = db.get(Tender, tender_id)
    if not tender:
        raise TenderNotFound(f"Tender with id '{tender_id}' not found")

    if not is_user_responsible_for_organization(db, requester.id, tender.organization_id):
        raise PermissionDenied(f"User '{requester_username}' does not have permission to view feedback for this tender")

    bids_query = select(Bid).where(
        Bid.author_id == author.id
    )
    bids = db.scalars(bids_query).all()

    if not bids:
        raise BidNotFound(f"No bids found for author '{author_username}'")

    feedback_query = select(BidFeedback).where(
        BidFeedback.bid_id.in_([bid.id for bid in bids])
    ).limit(limit).offset(offset)

    feedbacks = db.scalars(feedback_query).all()

    return feedbacks




