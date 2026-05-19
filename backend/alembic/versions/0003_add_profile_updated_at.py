"""
Migration 0003 — Thêm cột updated_at vào bảng profiles.

LÝ DO:
  ERD schema (docs/architecture/erd_schema.md) định nghĩa PROFILES.updated_at,
  nhưng migration 0001 không tạo cột này. Migration này đồng bộ lại.

  Dùng server_default=now() để điền giá trị cho tất cả rows hiện có.
  Đây là backward-compatible change — không ảnh hưởng dữ liệu đã có.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_add_profile_updated_at"
down_revision: Union[str, None] = "0002_fix_vector_column_and_constraints"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Thêm cột updated_at với server_default=now() để an toàn với rows hiện có.
    # onupdate sẽ được xử lý bởi SQLAlchemy ORM (không phải trigger DB).
    op.add_column(
        "profiles",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("profiles", "updated_at")
