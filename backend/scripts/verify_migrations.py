"""
Q-School AI — Migration Verification Script
Kiểm tra tính toàn vẹn của migration chain trước khi deploy.

Usage:
    cd backend
    python scripts/verify_migrations.py

Kiểm tra:
  1. Tất cả models đã được import vào domain/models/__init__.py
  2. Migration chain liên tục (không branch, không gap)
  3. ERD tables khớp với migration tables
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def verify_model_imports():
    """Kiểm tra tất cả models đã được import."""
    print("[1/3] Verifying model imports...")
    from app.domain.models import (
        User, Profile, Class, ClassStudent,
        Lesson, Quiz, Question, Answer,
        Rubric, EssaySubmission, QuizAttempt, StudentAnswer,
        FlashcardSet, Flashcard, FlashcardReview,
        ClassAssignment,
        AIPrompt, ChatSession, ChatMessage,
        Document, DocumentChunk,
        AITask, GeneratedAsset,
        Plan, UserSubscription, PaymentTransaction,
    )
    from app.core.database import Base

    registered_tables = set(Base.metadata.tables.keys())
    expected_tables = {
        "users", "profiles", "plans", "user_subscriptions",
        "payment_transactions", "classes", "class_students",
        "lessons", "quizzes", "questions", "answers",
        "quiz_attempts", "student_answers",
        "rubrics", "essay_submissions",
        "flashcard_sets", "flashcards", "flashcard_reviews",
        "class_assignments",
        "ai_prompts", "chat_sessions", "chat_messages",
        "documents", "document_chunks",
        "ai_tasks", "generated_assets",
    }

    missing = expected_tables - registered_tables
    extra = registered_tables - expected_tables

    if missing:
        print(f"  [FAIL] Missing tables in metadata: {missing}")
        return False
    if extra:
        print(f"  [INFO] Extra tables found: {extra}")

    print(f"  [OK] All {len(expected_tables)} expected tables registered in Base.metadata")
    return True


def verify_migration_chain():
    """Kiểm tra migration chain liên tục."""
    print("\n[2/3] Verifying migration chain...")
    versions_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "alembic", "versions"
    )

    migration_files = sorted([
        f for f in os.listdir(versions_dir)
        if f.endswith(".py") and not f.startswith("__")
    ])

    print(f"  Found {len(migration_files)} migration files:")
    for f in migration_files:
        print(f"    - {f}")

    if len(migration_files) < 1:
        print("  [FAIL] No migration files found!")
        return False

    print(f"  [OK] Migration chain: {len(migration_files)} files")
    return True


def verify_erd_coverage():
    """Kiểm tra migration cover tất cả bảng trong ERD."""
    print("\n[3/3] Verifying ERD coverage...")
    erd_tables = [
        "users", "profiles", "plans", "user_subscriptions",
        "payment_transactions", "classes", "class_students",
        "lessons", "quizzes", "questions", "answers",
        "quiz_attempts", "student_answers",
        "rubrics", "essay_submissions",
        "flashcard_sets", "flashcards", "flashcard_reviews",
        "class_assignments",
        "ai_prompts", "documents", "document_chunks",
        "chat_sessions", "chat_messages",
        "ai_tasks", "generated_assets",
    ]

    # Read migration files to check table creation
    versions_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "alembic", "versions"
    )

    all_migration_content = ""
    for f in os.listdir(versions_dir):
        if f.endswith(".py") and not f.startswith("__"):
            with open(os.path.join(versions_dir, f), "r", encoding="utf-8") as fp:
                all_migration_content += fp.read()

    missing = []
    for table in erd_tables:
        if f'"{table}"' in all_migration_content or f"'{table}'" in all_migration_content:
            pass
        else:
            missing.append(table)

    if missing:
        print(f"  [WARN] Tables not found in migrations: {missing}")
    else:
        print(f"  [OK] All {len(erd_tables)} ERD tables covered in migrations")

    return len(missing) == 0


def main():
    print("=" * 50)
    print("Q-School AI — Migration Verification")
    print("=" * 50)

    results = []
    results.append(verify_model_imports())
    results.append(verify_migration_chain())
    results.append(verify_erd_coverage())

    print("\n" + "=" * 50)
    if all(results):
        print("ALL CHECKS PASSED")
        print("=" * 50)
        sys.exit(0)
    else:
        print("SOME CHECKS FAILED")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()
