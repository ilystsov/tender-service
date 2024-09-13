from fastapi import APIRouter, Depends, HTTPException, Query
import fastapi
from uuid import UUID

from src.models import TenderCreate, TenderOut, TenderUpdate, TenderStatus, PaginationParameters, \
    TenderServiceType
from src.db.crud import (
    get_tenders,
    create_tender,
    get_tender_status,
    get_tenders_by_user,
    update_tender,
    update_tender_status,
    rollback_tender_version
)
from sqlalchemy.orm import Session
from src.dependencies import get_db
from src.exceptions import UserNotFound, PermissionDenied, TenderNotFound, TenderVersionNotFound

router = APIRouter(prefix="/api/tenders", tags=["Tenders"])

def handle_exception(e: Exception, status_code: int):
    raise HTTPException(
        status_code=status_code,
        detail=str(e)
    )

@router.get("/", response_model=list[TenderOut])
def get_all_tenders(
    service_type: list[TenderServiceType] | None = Query(None, description="Тип услуг для фильтрации тендеров."),
    pagination: PaginationParameters = Depends(),
    db: Session = Depends(get_db)
):
    try:
        tenders = get_tenders(db=db, service_type=service_type, limit=pagination.limit, offset=pagination.offset)
        return [TenderOut.from_orm(tender) for tender in tenders]
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)

@router.post("/new", response_model=TenderOut)
def create_new_tender(
    tender_data: TenderCreate,
    db: Session = Depends(get_db)
):
    try:
        tender = create_tender(db=db, tender_data=tender_data)
        return TenderOut.from_orm(tender)
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)

@router.get("/my", response_model=list[TenderOut])
def get_user_tenders(
    username: str,
    pagination: PaginationParameters = Depends(),
    db: Session = Depends(get_db)
):
    try:
        tenders = get_tenders_by_user(db=db, username=username, limit=pagination.limit, offset=pagination.offset)
        return [TenderOut.from_orm(tender) for tender in tenders]
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)

@router.get("/{tenderId}/status", response_model=TenderStatus)
def get_tender_current_status(
    tenderId: UUID,
    username: str,
    db: Session = Depends(get_db)
):
    try:
        tender_status = get_tender_status(db=db, tender_id=tenderId, username=username)
        return tender_status
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except TenderNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)

@router.put("/{tenderId}/status", response_model=TenderOut)
def update_tender_status_endpoint(
    tenderId: UUID,
    status: TenderStatus,
    username: str,
    db: Session = Depends(get_db)
):
    try:
        tender = update_tender_status(db=db, tender_id=tenderId, new_status=status, username=username)
        return TenderOut.from_orm(tender)
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except TenderNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)

@router.patch("/{tenderId}/edit", response_model=TenderOut)
def edit_tender(
    tenderId: UUID,
    tender_data: TenderUpdate,
    username: str,
    db: Session = Depends(get_db)
):
    try:
        tender = update_tender(db=db, tender_id=tenderId, tender_data=tender_data, username=username)
        return TenderOut.from_orm(tender)
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except TenderNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)

@router.put("/{tenderId}/rollback/{version}", response_model=TenderOut)
def rollback_tender(
    tenderId: UUID,
    version: int,
    username: str,
    db: Session = Depends(get_db)
):
    try:
        tender = rollback_tender_version(db=db, tender_id=tenderId, version=version, username=username)
        return TenderOut.from_orm(tender)
    except UserNotFound as e:
        handle_exception(e, fastapi.status.HTTP_401_UNAUTHORIZED)
    except PermissionDenied as e:
        handle_exception(e, fastapi.status.HTTP_403_FORBIDDEN)
    except TenderVersionNotFound as e:
        handle_exception(e, fastapi.status.HTTP_404_NOT_FOUND)
    except Exception as e:
        handle_exception(e, fastapi.status.HTTP_400_BAD_REQUEST)
