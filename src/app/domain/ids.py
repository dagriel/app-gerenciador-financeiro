"""Domain identifiers helpers.

We keep UUID generation in the domain to avoid coupling application/services to ORM modules.
"""

from __future__ import annotations

import uuid


def new_transfer_pair_id() -> str:
    """Generate a new UUID for transfer pair tracking."""
    return str(uuid.uuid4())
