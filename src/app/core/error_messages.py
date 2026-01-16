"""Compatibility shim for the error catalog.

Source of truth now lives in `app.domain.error_messages`.

We keep this module to avoid large, noisy refactors while the project evolves.
"""

from __future__ import annotations

from app.domain.error_messages import ErrorMessage

__all__ = ["ErrorMessage"]
