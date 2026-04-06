from datetime import date, timedelta

from app.database import Base, SessionLocal, engine
from app.models.transaction import Transaction, TransactionType
from app.models.user import User, UserRole
from app.services.auth_service import hash_password


ADMIN_EMAIL = "admin@finance.com"
ADMIN_PASSWORD = "Admin@123"


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if admin is None:
            admin = User(
                name="System Admin",
                email=ADMIN_EMAIL,
                hashed_password=hash_password(ADMIN_PASSWORD),
                role=UserRole.admin,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        existing_txn_count = db.query(Transaction).count()
        if existing_txn_count == 0:
            categories = [
                (TransactionType.income, "salary", 5000.0),
                (TransactionType.expense, "rent", 1200.0),
                (TransactionType.expense, "utilities", 250.0),
                (TransactionType.expense, "groceries", 450.0),
                (TransactionType.income, "freelance", 900.0),
                (TransactionType.expense, "transport", 150.0),
                (TransactionType.expense, "insurance", 300.0),
                (TransactionType.income, "bonus", 700.0),
                (TransactionType.expense, "entertainment", 180.0),
                (TransactionType.expense, "health", 220.0),
            ]
            today = date.today()
            for i, (txn_type, category, amount) in enumerate(categories):
                db.add(
                    Transaction(
                        amount=amount,
                        type=txn_type,
                        category=category,
                        date=today - timedelta(days=i),
                        notes=f"Sample transaction {i + 1}",
                        created_by=admin.id,
                    )
                )
            db.commit()

        print("Seed complete.")
        print(f"Admin email: {ADMIN_EMAIL}")
        print(f"Admin password: {ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
