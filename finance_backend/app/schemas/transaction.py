from datetime import date as dt_date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..models.transaction import TransactionType


class TransactionBase(BaseModel):
    amount: float = Field(gt=0)
    type: TransactionType
    category: str
    date: dt_date
    notes: str | None = None

    @field_validator("date")
    @classmethod
    def validate_date_not_future(cls, value: dt_date) -> dt_date:
        if value > dt_date.today():
            raise ValueError("date cannot be in the future")
        return value


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    type: TransactionType | None = None
    category: str | None = None
    date: dt_date | None = None
    notes: str | None = None

    @field_validator("date")
    @classmethod
    def validate_optional_date_not_future(cls, value: dt_date | None) -> dt_date | None:
        if value and value > dt_date.today():
            raise ValueError("date cannot be in the future")
        return value


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: float
    type: TransactionType
    category: str
    date: dt_date
    notes: str | None
    created_by: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class CategorySummary(BaseModel):
    category: str
    total_amount: float
    count: int


class TrendSummary(BaseModel):
    month: str
    income: float
    expense: float


class DashboardSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    total_transactions: int
