from datetime import date as dt_date
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from ..core.access_control import require_role
from ..database import get_db
from ..models.transaction import Transaction, TransactionType
from ..models.user import User, UserRole
from ..schemas.transaction import (
    CategorySummary,
    DashboardSummary,
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
    TrendSummary,
)
from ..services import dashboard_service, transaction_service


router = APIRouter(tags=["Transactions and Dashboard"])


@router.get("/api/transactions", response_model=list[TransactionRead])
def list_transactions(
    category: str | None = None,
    type: TransactionType | None = None,
    from_date: dt_date | None = None,
    to_date: dt_date | None = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.analyst, UserRole.admin)),
) -> list[Transaction]:
    return transaction_service.list_transactions(
        db,
        page=page,
        limit=limit,
        category=category,
        txn_type=type,
        from_date=from_date,
        to_date=to_date,
    )


@router.post("/api/transactions", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: User = Depends(require_role(UserRole.admin)),
) -> Transaction:
    return transaction_service.create_transaction(db, payload, creator_id=current_user.id)


@router.get("/api/transactions/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: User = Depends(require_role(UserRole.analyst, UserRole.admin)),
) -> Transaction:
    return transaction_service.get_transaction_or_404(db, transaction_id)


@router.put("/api/transactions/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: User = Depends(require_role(UserRole.admin)),
) -> Transaction:
    return transaction_service.update_transaction(db, transaction_id, payload)


@router.delete("/api/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: User = Depends(require_role(UserRole.admin)),
) -> Response:
    transaction_service.soft_delete_transaction(db, transaction_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/api/dashboard/summary", response_model=DashboardSummary)
def get_summary(
    db: Annotated[Session, Depends(get_db)],
    _: User = Depends(require_role(UserRole.viewer, UserRole.analyst, UserRole.admin)),
) -> dict:
    return dashboard_service.summary(db)


@router.get("/api/dashboard/by-category", response_model=list[CategorySummary])
def get_by_category(
    db: Annotated[Session, Depends(get_db)],
    _: User = Depends(require_role(UserRole.analyst, UserRole.admin)),
) -> list[dict]:
    return dashboard_service.by_category(db)


@router.get("/api/dashboard/trends", response_model=list[TrendSummary])
def get_trends(
    db: Annotated[Session, Depends(get_db)],
    _: User = Depends(require_role(UserRole.analyst, UserRole.admin)),
) -> list[dict]:
    return dashboard_service.trends(db)


@router.get("/api/dashboard/recent", response_model=list[TransactionRead])
def get_recent(
    db: Annotated[Session, Depends(get_db)],
    _: User = Depends(require_role(UserRole.analyst, UserRole.admin)),
) -> list[Transaction]:
    return dashboard_service.recent(db)
