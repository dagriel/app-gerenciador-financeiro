"""Account schemas."""

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    """Schema for creating an account."""

    name: str = Field(..., min_length=1, max_length=120, examples=["Banco"])
    type: str = Field(
        default="BANK",
        min_length=1,
        max_length=40,
        description="Tipo livre no MVP. Valores recomendados: BANK, CASH.",
        examples=["BANK", "CASH"],
    )


class AccountUpdate(BaseModel):
    """Schema for updating an account."""

    name: str | None = Field(default=None, min_length=1, max_length=120, examples=["Banco"])
    type: str | None = Field(
        default=None,
        min_length=1,
        max_length=40,
        description="Tipo livre no MVP. Valores recomendados: BANK, CASH.",
        examples=["BANK", "CASH"],
    )
    active: bool | None = None


class AccountOut(BaseModel):
    """Schema for account response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    active: bool
