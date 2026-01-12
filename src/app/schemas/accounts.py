"""Account schemas."""

from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    """Schema for creating an account."""

    name: str
    type: str = "BANK"


class AccountUpdate(BaseModel):
    """Schema for updating an account."""

    name: str | None = None
    type: str | None = None
    active: bool | None = None


class AccountOut(BaseModel):
    """Schema for account response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    active: bool
