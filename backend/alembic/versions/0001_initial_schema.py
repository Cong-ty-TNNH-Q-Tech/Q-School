"""
Initial Migration — Tạo toàn bộ bảng lần đầu tiên.
Bao gồm: pgvector extension + HNSW index cho document_chunks.

Tạo bằng: alembic revision --autogenerate -m "initial_schema"
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ─── Enable pgvector extension ───
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ─── USERS ───
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("username", sa.String(50), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="student"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("role IN ('student', 'teacher', 'admin')", name="ck_users_role"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_deleted_at", "users", ["deleted_at"])

    # ─── PROFILES ───
    op.create_table(
        "profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("school_name", sa.String(255), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
    )

    # ─── PLANS ───
    op.create_table(
        "plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("billing_cycle", sa.String(20), nullable=False, server_default="monthly"),
        sa.Column("price", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("features", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )

    # ─── USER_SUBSCRIPTIONS ───
    op.create_table(
        "user_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("status IN ('active', 'past_due', 'canceled')", name="ck_user_subscriptions_status"),
    )
    op.create_index("ix_user_subscriptions_user_id", "user_subscriptions", ["user_id"])
    op.create_index("ix_user_subscriptions_user_status", "user_subscriptions", ["user_id", "status"])

    # ─── PAYMENT_TRANSACTIONS ───
    op.create_table(
        "payment_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("user_subscriptions.id"), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(10), nullable=False, server_default="VND"),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("provider_transaction_id", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("provider IN ('stripe', 'vnpay', 'momo')", name="ck_payment_transactions_provider"),
        sa.CheckConstraint("status IN ('pending', 'success', 'failed')", name="ck_payment_transactions_status"),
    )

    # ─── CLASSES ───
    op.create_table(
        "classes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("grade_level", sa.String(20), nullable=True),
        sa.Column("subject", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_classes_teacher_id", "classes", ["teacher_id"])

    # ─── CLASS_STUDENTS ───
    op.create_table(
        "class_students",
        sa.Column("class_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classes.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    # PK tự có index (class_id, student_id). Thêm index riêng cho student_id để query ngược lại.
    op.create_index("ix_class_students_student_id", "class_students", ["student_id"])

    # ─── LESSONS ───
    op.create_table(
        "lessons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("subject", sa.String(100), nullable=True),
        sa.Column("grade_level", sa.String(20), nullable=True),
        sa.Column("content", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ─── QUIZZES ───
    op.create_table(
        "quizzes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content_source", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ─── QUESTIONS ───
    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("quiz_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("media_url", sa.String(512), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )

    # ─── ANSWERS ───
    op.create_table(
        "answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("media_url", sa.String(512), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default="false"),
    )

    # ─── RUBRICS ───
    op.create_table(
        "rubrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("criteria_matrix", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ─── ESSAY_SUBMISSIONS ───
    op.create_table(
        "essay_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("rubric_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rubrics.id"), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("ai_feedback", postgresql.JSONB(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ─── QUIZ_ATTEMPTS ───
    op.create_table(
        "quiz_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("quiz_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quizzes.id"), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ─── STUDENT_ANSWERS ───
    op.create_table(
        "student_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("attempt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("selected_answer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("answers.id"), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.UniqueConstraint("attempt_id", "question_id", name="uq_student_answer_attempt_question"),
    )
    op.create_index("ix_student_answers_attempt_id", "student_answers", ["attempt_id"])

    # ─── FLASHCARD_SETS ───
    op.create_table(
        "flashcard_sets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ─── FLASHCARDS ───
    op.create_table(
        "flashcards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("set_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("flashcard_sets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("front_text", sa.Text(), nullable=False),
        sa.Column("back_text", sa.Text(), nullable=False),
        sa.Column("media_url", sa.String(512), nullable=True),
    )

    # ─── FLASHCARD_REVIEWS ───
    op.create_table(
        "flashcard_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("flashcard_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False),
        sa.Column("confidence_level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("student_id", "flashcard_id", name="uq_flashcard_review_student_card"),
    )

    # ─── CLASS_ASSIGNMENTS ───
    op.create_table(
        "class_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resource_type", sa.String(20), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("unlock_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("resource_type IN ('lesson', 'quiz')", name="ck_class_assignments_resource_type"),
    )
    op.create_index("ix_class_assignments_class_id", "class_assignments", ["class_id"])
    op.create_index("ix_class_assignments_resource", "class_assignments", ["resource_type", "resource_id"])
    op.create_index("ix_class_assignments_due_date", "class_assignments", ["due_date"])      # reminder jobs
    op.create_index("ix_class_assignments_unlock_date", "class_assignments", ["unlock_date"]) # cron mở bài

    # ─── AI_PROMPTS ───
    op.create_table(
        "ai_prompts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("persona_name", sa.String(100), nullable=False, unique=True),
        sa.Column("system_prompt_template", sa.Text(), nullable=False),
        sa.Column("version", sa.String(20), nullable=False, server_default="v1.0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ─── DOCUMENTS ───
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("uploader_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("file_type", sa.String(20), nullable=False),
        sa.Column("s3_url", sa.String(1024), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # ─── DOCUMENT_CHUNKS (pgvector) ───
    op.create_table(
        "document_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("embedding_vector", sa.Text(), nullable=True),  # pgvector type
        sa.Column("chunk_index", sa.Integer(), nullable=False, server_default="0"),
    )
    # Đổi sang pgvector type và tạo HNSW Index
    op.execute("ALTER TABLE document_chunks ALTER COLUMN embedding_vector TYPE vector(1536) USING NULL::vector(1536)")
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding_hnsw "
        "ON document_chunks USING hnsw (embedding_vector vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )

    # ─── CHAT_SESSIONS ───
    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("ai_persona", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ─── CHAT_MESSAGES ───
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_type", sa.String(10), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("sender_type IN ('user', 'ai')", name="ck_chat_messages_sender_type"),
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"])

    # ─── AI_TASKS ───
    op.create_table(
        "ai_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("task_type", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("result_payload", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_ai_tasks_user_id", "ai_tasks", ["user_id"])
    op.create_index("ix_ai_tasks_status", "ai_tasks", ["status"])  # Query tasks pending/processing

    # ─── GENERATED_ASSETS ───
    op.create_table(
        "generated_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("asset_type", sa.String(50), nullable=False),
        sa.Column("input_params", postgresql.JSONB(), nullable=True),
        sa.Column("output_content", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ─── Seed default Plans ───
    op.execute("""
        INSERT INTO plans (id, name, billing_cycle, price, features, is_active) VALUES
        (gen_random_uuid(), 'Free', 'monthly', 0, '{"max_ai_chat_per_day": 5, "max_documents": 3, "max_classes": 2}', true),
        (gen_random_uuid(), 'Pro', 'monthly', 99000, '{"max_ai_chat_per_day": 100, "max_documents": 50, "max_classes": 20}', true),
        (gen_random_uuid(), 'Enterprise', 'monthly', 299000, '{"max_ai_chat_per_day": -1, "max_documents": -1, "max_classes": -1}', true)
    """)

    # ─── Seed default AI Personas ───
    op.execute("""
        INSERT INTO ai_prompts (id, persona_name, system_prompt_template, version) VALUES
        (gen_random_uuid(), 'Raina', 'Bạn là Raina, trợ lý sư phạm AI của Q-School. Bạn thân thiện, chuyên nghiệp và luôn hỗ trợ giáo viên trong việc soạn bài giảng và đánh giá học sinh. {context}', 'v1.0'),
        (gen_random_uuid(), 'Tutor', 'Bạn là AI Tutor của Q-School, chuyên hỗ trợ học sinh học tập 1-1. Giải thích dễ hiểu, khuyến khích tư duy phản biện. Môn học: {subject}. {context}', 'v1.0'),
        (gen_random_uuid(), 'StudyBot', 'Bạn là StudyBot, trợ lý ôn tập của Q-School. Giúp học sinh ôn tập bằng câu hỏi, flashcard và tóm tắt kiến thức. {context}', 'v1.0')
    """)


def downgrade() -> None:
    # Xóa theo thứ tự ngược lại (từ dependent đến independent)
    op.drop_table("generated_assets")
    op.drop_table("ai_tasks")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.drop_table("ai_prompts")
    op.drop_table("class_assignments")
    op.drop_table("flashcard_reviews")
    op.drop_table("flashcards")
    op.drop_table("flashcard_sets")
    op.drop_table("student_answers")
    op.drop_table("quiz_attempts")
    op.drop_table("essay_submissions")
    op.drop_table("rubrics")
    op.drop_table("answers")
    op.drop_table("questions")
    op.drop_table("quizzes")
    op.drop_table("lessons")
    op.drop_table("class_students")
    op.drop_table("classes")
    op.drop_table("payment_transactions")
    op.drop_table("user_subscriptions")
    op.drop_table("plans")
    op.drop_table("profiles")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")
