"""role update start/end

Revision ID: 987cdaf01bd2
Revises: 45a78aed088b
Create Date: 2025-11-25 11:44:36.810832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '987cdaf01bd2'
down_revision: Union[str, Sequence[str], None] = '45a78aed088b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new values to existing enum type
    op.execute("ALTER TYPE waypoint_role ADD VALUE IF NOT EXISTS 'START';")
    op.execute("ALTER TYPE waypoint_role ADD VALUE IF NOT EXISTS 'END';")

    # Update default to REQUIRED
    op.alter_column(
        "waypoints",
        "role",
        server_default="REQUIRED",
        existing_nullable=False,
    )


def downgrade() -> None:
    # You *cannot* easily remove values from a Postgres enum.
    # If you really need full downgrade, you'd have to recreate the type.
    # For your project it's fine to only revert the default:

    op.alter_column(
        "waypoints",
        "role",
        server_default=sa.text("'OPTIONAL'::waypoint_role"),
        existing_nullable=False,
    )