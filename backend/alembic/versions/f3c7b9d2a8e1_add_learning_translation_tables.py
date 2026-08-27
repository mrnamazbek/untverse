"""Add normalized translations for curriculum content.

Revision ID: f3c7b9d2a8e1
Revises: d7d3f0e03298
Create Date: 2026-08-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f3c7b9d2a8e1"
down_revision: Union[str, None] = "d7d3f0e03298"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "course_translations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(length=5), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_id", "locale", name="uq_course_translation_locale"),
    )
    op.create_index(op.f("ix_course_translations_course_id"), "course_translations", ["course_id"])
    op.create_index(op.f("ix_course_translations_locale"), "course_translations", ["locale"])

    op.create_table(
        "topic_translations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(length=5), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("topic_id", "locale", name="uq_topic_translation_locale"),
    )
    op.create_index(op.f("ix_topic_translations_topic_id"), "topic_translations", ["topic_id"])
    op.create_index(op.f("ix_topic_translations_locale"), "topic_translations", ["locale"])

    op.create_table(
        "lesson_translations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(length=5), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lesson_id", "locale", name="uq_lesson_translation_locale"),
    )
    op.create_index(op.f("ix_lesson_translations_lesson_id"), "lesson_translations", ["lesson_id"])
    op.create_index(op.f("ix_lesson_translations_locale"), "lesson_translations", ["locale"])


def downgrade() -> None:
    op.drop_index(op.f("ix_lesson_translations_locale"), table_name="lesson_translations")
    op.drop_index(op.f("ix_lesson_translations_lesson_id"), table_name="lesson_translations")
    op.drop_table("lesson_translations")
    op.drop_index(op.f("ix_topic_translations_locale"), table_name="topic_translations")
    op.drop_index(op.f("ix_topic_translations_topic_id"), table_name="topic_translations")
    op.drop_table("topic_translations")
    op.drop_index(op.f("ix_course_translations_locale"), table_name="course_translations")
    op.drop_index(op.f("ix_course_translations_course_id"), table_name="course_translations")
    op.drop_table("course_translations")
