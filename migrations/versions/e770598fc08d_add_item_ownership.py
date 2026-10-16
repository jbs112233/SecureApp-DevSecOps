"""add item ownership

Revision ID: e770598fc08d
Revises: ab148143cd93
"""

from alembic import op
import sqlalchemy as sa


revision = "e770598fc08d"
down_revision = "ab148143cd93"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add owner_id using SQLite-compatible batch migration."""
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    columns = {
        column["name"]
        for column in inspector.get_columns("items")
    }

    indexes = {
        index["name"]
        for index in inspector.get_indexes("items")
    }

    foreign_keys = inspector.get_foreign_keys("items")

    with op.batch_alter_table("items", recreate="always") as batch_op:
        if "owner_id" not in columns:
            batch_op.add_column(
                sa.Column("owner_id", sa.Integer(), nullable=True)
            )

        if "ix_items_owner_id" not in indexes:
            batch_op.create_index(
                "ix_items_owner_id",
                ["owner_id"],
                unique=False,
            )

        has_owner_foreign_key = any(
            fk.get("constrained_columns") == ["owner_id"]
            and fk.get("referred_table") == "users"
            and fk.get("referred_columns") == ["id"]
            for fk in foreign_keys
        )

        if not has_owner_foreign_key:
            batch_op.create_foreign_key(
                "fk_items_owner_id_users",
                "users",
                ["owner_id"],
                ["id"],
            )


def downgrade() -> None:
    """Remove item ownership."""
    with op.batch_alter_table("items", recreate="always") as batch_op:
        batch_op.drop_constraint(
            "fk_items_owner_id_users",
            type_="foreignkey",
        )
        batch_op.drop_index("ix_items_owner_id")
        batch_op.drop_column("owner_id")
