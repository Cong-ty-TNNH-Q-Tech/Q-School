"""
Migration 0002 — Fix embedding_vector column type và thêm CheckConstraints còn thiếu.

THAY ĐỔI:
  1. document_chunks.embedding_vector: Text → vector(1536)
     Lý do: 0001 tạo nhầm kiểu TEXT thay vì pgvector Vector type.
     USING NULL::vector(1536) — safe vì migration 0001 tạo cột nullable=True, không có data thật.

  2. Thêm CheckConstraint cho ai_tasks.status và ai_tasks.task_type
     Lý do: DB-level validation để tránh worker insert giá trị sai.

  3. Thêm CheckConstraint cho generated_assets.asset_type
     Lý do: Consistency với các bảng khác (users.role, payment_transactions.status).
"""
from typing import Sequence, Union

from alembic import op


revision: str = "0002_fix_vector_constraints"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── 1. Đảm bảo embedding_vector là vector(1536) ───
    # NOTE: Migration 0001 đã tạo cột TEXT rồi ALTER thành vector(1536) trong cùng migration.
    # ALTER này là REDUNDANT (idempotent - không gây lỗi, chỉ no-op) nhưng giữ lại
    # để migration chain chính xác. Xem 0001 line 302 để biết ALTER gốc.
    op.execute(
        "ALTER TABLE document_chunks "
        "ALTER COLUMN embedding_vector TYPE vector(1536) "
        "USING NULL::vector(1536)"
    )

    # ─── 2. CheckConstraints cho ai_tasks ───
    op.create_check_constraint(
        "ck_ai_tasks_status",
        "ai_tasks",
        "status IN ('pending', 'processing', 'completed', 'failed')",
    )
    op.create_check_constraint(
        "ck_ai_tasks_task_type",
        "ai_tasks",
        "task_type IN ('essay_grading', 'lesson_plan', 'parse_document', 'quiz_generation')",
    )

    # ─── 3. CheckConstraint cho generated_assets ───
    op.create_check_constraint(
        "ck_generated_assets_asset_type",
        "generated_assets",
        "asset_type IN ('lesson_plan', 'quiz', 'email', 'iep', 'behavior_intervention', 'report_comment')",
    )


def downgrade() -> None:
    # Xóa constraints
    op.drop_constraint("ck_generated_assets_asset_type", "generated_assets")
    op.drop_constraint("ck_ai_tasks_task_type", "ai_tasks")
    op.drop_constraint("ck_ai_tasks_status", "ai_tasks")

    # Revert vector → text (mất semantics nhưng structurally valid)
    op.execute(
        "ALTER TABLE document_chunks "
        "ALTER COLUMN embedding_vector TYPE TEXT "
        "USING NULL"
    )
