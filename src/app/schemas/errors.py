"""Error response schemas (API contract).

This project standardizes error responses using a Problem Details-like structure
(inspired by RFC 7807) to provide a stable contract for clients and better
Swagger/OpenAPI documentation.

FastAPI defaults:
- HTTPException -> {"detail": "..."}
- RequestValidationError (422) -> {"detail": [ ... ]}

We override those via exception handlers to return the schema below.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProblemDetail(BaseModel):
    """Standard error payload for the API."""

    model_config = ConfigDict(extra="forbid")

    status: int = Field(..., description="HTTP status code.")
    title: str = Field(..., description="Short, human-readable summary of the problem.")
    detail: str = Field(..., description="Human-readable explanation specific to this occurrence.")
    code: str | None = Field(
        default=None,
        description="Stable machine-readable error code (recommended for clients).",
        examples=["TX_NOT_FOUND", "API_KEY_INVALID"],
    )
    instance: str = Field(
        ...,
        description="Request path (instance) where the error occurred.",
        examples=["/transactions/123"],
    )
    errors: list[dict] | None = Field(
        default=None,
        description="Optional structured validation errors (mainly for 422 validation).",
        examples=[
            [
                {
                    "loc": ["body", "amount_planned"],
                    "msg": "Input should be greater than 0",
                    "type": "greater_than",
                }
            ]
        ],
    )
