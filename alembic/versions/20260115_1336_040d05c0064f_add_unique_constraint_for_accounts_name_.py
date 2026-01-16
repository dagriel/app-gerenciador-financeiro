"""add unique constraint for accounts name+type

Revision ID: 040d05c0064f
Revises: c6d8e0a58a94
Create Date: 2026-01-15 13:36:40.374141

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '040d05c0064f'
down_revision = 'c6d8e0a58a94'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite does not support ALTER TABLE ADD CONSTRAINT directly.
    # Use Alembic batch mode (copy-and-move strategy).
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.create_unique_constraint("uq_account_name_type", ["name", "type"])


def downgrade() -> None:
    # SQLite batch mode for dropping constraints.
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.drop_constraint("uq_account_name_type", type_="unique")
