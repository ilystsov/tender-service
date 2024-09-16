import fastapi
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from src.db.models import BidDecisionStatus, BidFeedback
from src.models import BidCreate, BidOut, BidUpdate, BidStatus, PaginationParameters, BidFeedbackOut
from src.db.crud import (
    create_bid,
    get_bids_by_user,
    get_bids_for_tender,
    get_bid_status,
    update_bid_status,
    update_bid,
    rollback_bid_version,
    submit_bid_feedback,
    submit_bid_decision,
    get_bid_feedbacks,
)
from src.dependencies import get_db
from src.exceptions import UserNotFound, PermissionDenied, TenderNotFound, BidNotFound, BidVersionNotFound

router = APIRouter(prefix="/api/bids", tags=["Bids"])

def handle_exception(e: Exception, status_code: int):
    raise HTTPException(
        status_code=status_code,
        detail=str(e)
    )

@router.post("/new", response_model=BidOut)
def create_new_bid(
    bid_data: BidCreate,
    db: Session = Depends(get_db)
):
    try:
        bid = create_bid(db=db, bid_data=bid_data)
        return BidOut.from_orm(bid)
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except TenderNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)

@router.get("/my", response_model=list[BidOut])
def get_user_bids(
    username: str,
    pagination: PaginationParameters = Depends(),
    db: Session = Depends(get_db)
):
    try:
        bids = get_bids_by_user(db=db, username=username, limit=pagination.limit, offset=pagination.offset)
        return [BidOut.from_orm(bid) for bid in bids]
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)

@router.get("/{tenderId}/list", response_model=list[BidOut])
def get_bids_for_tender_endpoint(
    tenderId: UUID,
    username: str,
    pagination: PaginationParameters = Depends(),
    db: Session = Depends(get_db)
):
    try:
        bids = get_bids_for_tender(db=db, tender_id=tenderId, username=username, limit=pagination.limit, offset=pagination.offset)
        return [BidOut.from_orm(bid) for bid in bids]
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except TenderNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)

@router.get("/{bidId}/status", response_model=BidStatus)
def get_bid_status_endpoint(
    bidId: UUID,
    username: str,
    db: Session = Depends(get_db)
):
    try:
        bid_status = get_bid_status(db=db, bid_id=bidId, username=username)
        return bid_status
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except BidNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)

@router.put("/{bidId}/status", response_model=BidOut)
def update_bid_status_endpoint(
    bidId: UUID,
    status: BidStatus,
    username: str,
    db: Session = Depends(get_db)
):
    try:
        bid = update_bid_status(db=db, bid_id=bidId, new_status=status, username=username)
        return BidOut.from_orm(bid)
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except BidNotFound as e:  # Исправлено: проверка на существование предложения
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)





@router.patch("/{bidId}/edit", response_model=BidOut)
def edit_bid(
    bidId: UUID,
    bid_data: BidUpdate,
    username: str,
    db: Session = Depends(get_db)
):
    try:
        bid = update_bid(db=db, bid_id=bidId, bid_data=bid_data, username=username)
        return BidOut.from_orm(bid)
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except BidNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)


@router.put("/{bidId}/submit_decision", response_model=BidOut)
def submit_bid_decision_endpoint(
    bidId: UUID,
    decision: BidDecisionStatus,
    username: str,
    db: Session = Depends(get_db)
):
    try:
        bid = submit_bid_decision(db=db, bid_id=bidId, decision=decision, username=username)
        return BidOut.from_orm(bid)
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except BidNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)


@router.put("/{bidId}/feedback", response_model=BidOut)
def submit_bid_feedback_endpoint(
    bidId: UUID,
    bidFeedback: str,
    username: str,
    db: Session = Depends(get_db)
):
    try:
        bid = submit_bid_feedback(db=db, bid_id=bidId, feedback_text=bidFeedback, username=username)
        return BidOut.from_orm(bid)
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except BidNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)


@router.put("/{bidId}/rollback/{version}", response_model=BidOut)
def rollback_bid_version_endpoint(
    bidId: UUID,
    version: int,
    username: str,
    db: Session = Depends(get_db)
):
    try:
        bid = rollback_bid_version(db=db, bid_id=bidId, version=version, username=username)
        return BidOut.from_orm(bid)
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except BidVersionNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except BidNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)


@router.get("/{tenderId}/reviews", response_model=list[BidFeedbackOut])
def get_bid_reviews(
    tenderId: UUID,
    authorUsername: str,
    requesterUsername: str,
    pagination: PaginationParameters = Depends(),
    db: Session = Depends(get_db)
):
    try:
        feedbacks = get_bid_feedbacks(
            db=db,
            tender_id=tenderId,
            author_username=authorUsername,
            requester_username=requesterUsername,
            limit=pagination.limit,
            offset=pagination.offset
        )
        return [BidFeedbackOut.from_orm(feedback) for feedback in feedbacks]
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except TenderNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)