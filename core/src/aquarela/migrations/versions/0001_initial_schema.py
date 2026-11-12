"""initial schema

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("root_path", sa.Text, nullable=False),
        sa.Column("created_at", sa.BigInteger, nullable=False),
        sa.Column("updated_at", sa.BigInteger, nullable=False),
    )
    op.create_table(
        "classes",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column(
            "project_id",
            sa.Text,
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("color", sa.Text, nullable=False),
        sa.Column("hotkey", sa.Text),
        sa.Column("position", sa.Integer, nullable=False),
        sa.UniqueConstraint("project_id", "name"),
        sa.UniqueConstraint("project_id", "hotkey"),
    )
    op.create_table(
        "images",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column(
            "project_id",
            sa.Text,
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rel_path", sa.Text, nullable=False),
        sa.Column("width", sa.Integer, nullable=False),
        sa.Column("height", sa.Integer, nullable=False),
        sa.Column("status", sa.Text, nullable=False, server_default="todo"),
        sa.Column("created_at", sa.BigInteger, nullable=False),
        sa.Column("updated_at", sa.BigInteger, nullable=False),
        sa.CheckConstraint("status IN ('todo', 'in_progress', 'in_review', 'done')"),
        sa.UniqueConstraint("project_id", "rel_path"),
    )
    op.create_index("images_page", "images", ["project_id", "status", "id"])
    op.create_table(
        "annotations",
        sa.Column(
            "image_id",
            sa.Text,
            sa.ForeignKey("images.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("shapes", sa.Text, nullable=False),
        sa.Column("updated_at", sa.BigInteger, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("annotations")
    op.drop_index("images_page", table_name="images")
    op.drop_table("images")
    op.drop_table("classes")
    op.drop_table("projects")
