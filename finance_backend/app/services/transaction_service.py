from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.transaction import Transaction, TransactionType
from ..schemas.transaction import TransactionCreate, TransactionUpdate


def create_transaction(db: Session, payload: TransactionCreate, creator_id: int) -> Transaction:
    txn = Transaction(
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        date=payload.date,
        notes=payload.notes,
        created_by=creator_id,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def list_transactions(
    db: Session,
    page: int,
    limit: int,
    category: str | None = None,
    txn_type: TransactionType | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[Transaction]:
    query = db.query(Transaction).filter(Transaction.is_deleted.is_(False))

    if category:
        query = query.filter(Transaction.category == category)
    if txn_type:
        query = query.filter(Transaction.type == txn_type)
    if from_date:
        query = query.filter(Transaction.date >= from_date)
    if to_date:
        query = query.filter(Transaction.date <= to_date)

    offset = (page - 1) * limit
    return query.order_by(Transaction.date.desc(), Transaction.id.desc()).offset(offset).limit(limit).all()


def get_transaction_or_404(db: Session, transaction_id: int) -> Transaction:
    txn = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.is_deleted.is_(False))
        .first()
    )
    if txn is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return txn


def update_transaction(db: Session, transaction_id: int, payload: TransactionUpdate) -> Transaction:
    txn = get_transaction_or_404(db, transaction_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(txn, field, value)

    db.commit()
    db.refresh(txn)
    return txn


def soft_delete_transaction(db: Session, transaction_id: int) -> None:
    txn = get_transaction_or_404(db, transaction_id)
    txn.is_deleted = True
    db.commit()
