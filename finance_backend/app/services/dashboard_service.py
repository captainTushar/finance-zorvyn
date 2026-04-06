from collections import defaultdict

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from ..models.transaction import Transaction, TransactionType


def summary(db: Session) -> dict:
    totals = (
        db.query(
            func.coalesce(
                func.sum(case((Transaction.type == TransactionType.income, Transaction.amount), else_=0.0)),
                0.0,
            ).label("total_income"),
            func.coalesce(
                func.sum(case((Transaction.type == TransactionType.expense, Transaction.amount), else_=0.0)),
                0.0,
            ).label("total_expenses"),
            func.count(Transaction.id).label("total_transactions"),
        )
        .filter(Transaction.is_deleted.is_(False))
        .one()
    )

    total_income = float(totals.total_income or 0.0)
    total_expenses = float(totals.total_expenses or 0.0)
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": total_income - total_expenses,
        "total_transactions": int(totals.total_transactions or 0),
    }


def by_category(db: Session) -> list[dict]:
    rows = (
        db.query(
            Transaction.category.label("category"),
            func.coalesce(func.sum(Transaction.amount), 0.0).label("total_amount"),
            func.count(Transaction.id).label("count"),
        )
        .filter(Transaction.is_deleted.is_(False))
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    return [
        {
            "category": row.category,
            "total_amount": float(row.total_amount),
            "count": int(row.count),
        }
        for row in rows
    ]


def trends(db: Session) -> list[dict]:
    month_expr = func.strftime("%Y-%m", Transaction.date)
    rows = (
        db.query(
            month_expr.label("month"),
            Transaction.type.label("type"),
            func.coalesce(func.sum(Transaction.amount), 0.0).label("total"),
        )
        .filter(Transaction.is_deleted.is_(False))
        .group_by(month_expr, Transaction.type)
        .order_by(month_expr.asc())
        .all()
    )

    grouped: dict[str, dict[str, float]] = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for row in rows:
        grouped[row.month][row.type.value] = float(row.total)

    return [
        {"month": month, "income": values["income"], "expense": values["expense"]}
        for month, values in grouped.items()
    ]


def recent(db: Session) -> list[Transaction]:
    return (
        db.query(Transaction)
        .filter(Transaction.is_deleted.is_(False))
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .limit(10)
        .all()
    )
