"""add image expiration columns

Revision ID: 8c2f9d4a1b6e
Revises: 77e707154a24
Create Date: 2026-04-18 18:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8c2f9d4a1b6e"
down_revision: Union[str, Sequence[str], None] = "77e707154a24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("radiographies", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_public",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("1"),
            )
        )
        batch_op.add_column(
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.create_index(
            batch_op.f("ix_radiographies_expires_at"),
            ["expires_at"],
            unique=False,
        )

    op.execute(
        """
        UPDATE radiographies
        SET expires_at = datetime(created_at, '+1 day')
        WHERE expires_at IS NULL
        """
    )

    with op.batch_alter_table("radiographies", schema=None) as batch_op:
        batch_op.alter_column(
            "expires_at",
            existing_type=sa.DateTime(timezone=True),
            nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("radiographies", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_radiographies_expires_at"))
        batch_op.drop_column("expires_at")
        batch_op.drop_column("is_public")
