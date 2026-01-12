"""Budget schemas."""

from pydantic import BaseModel, ConfigDict, Field


class BudgetUpsert(BaseModel):
    """Schema for creating/updating a budget."""

    month: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    category_id: int
    amount_planned: float = Field(..., gt=0)


class BudgetOut(BaseModel):
    """Schema for budget response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    month: str
    category_id: int
    amount_planned: float
