"""add geography geom to users and jobs

Revision ID: 3fddd82365de
Revises: 40b2af8aa2f7
Create Date: 2025-10-20 20:01:49.048812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fddd82365de'
down_revision: Union[str, Sequence[str], None] = '40b2af8aa2f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
