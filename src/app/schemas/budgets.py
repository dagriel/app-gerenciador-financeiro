"""Budget schemas."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.validators import parse_month_str
from app.schemas.types import MoneyDecimal


class BudgetUpsert(BaseModel):
    """Schema for creating/updating a budget."""

    month: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}$",
        description="Mês no formato YYYY-MM.",
        examples=["2026-01"],
    )
    category_id: int = Field(..., examples=[1])
    amount_planned: MoneyDecimal = Field(
        ...,
        gt=0,
        description="Valor planejado (sempre positivo). Preferencialmente enviar como string.",
        examples=["500.00"],
    )

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: str) -> str:
        parse_month_str(v)
        return v


class BudgetOut(BaseModel):
    """Schema for budget response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    month: str
    category_id: int
    amount_planned: MoneyDecimal
