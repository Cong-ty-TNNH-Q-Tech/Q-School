# Alembic Migrations — Q-School AI

## Tổng quan

Dự án sử dụng **Alembic** cho database migrations với **async engine** (asyncpg).

## Cấu trúc

```
backend/
├── alembic.ini                    # Alembic configuration
├── alembic/
│   ├── env.py                     # Migration environment (async support)
│   ├── script.py.mako             # Template cho migration mới
│   └── versions/
│       ├── 0001_initial_schema.py           # 17+ bảng + pgvector + seed data
│       ├── 0002_fix_vector_column_and_constraints.py  # Fix constraints
│       └── 0003_add_profile_updated_at.py   # Thêm profiles.updated_at
```

## Danh sách bảng (17 bảng chính)

| # | Bảng | Mô tả | Seed Data |
|---|------|-------|-----------|
| 1 | `users` | Tài khoản (student, teacher, admin) | - |
| 2 | `profiles` | Hồ sơ cá nhân (1:1 với users) | - |
| 3 | `plans` | Gói cước SaaS | Free, Pro, Enterprise |
| 4 | `user_subscriptions` | Subscription lifecycle | - |
| 5 | `payment_transactions` | Lịch sử thanh toán | - |
| 6 | `classes` | Lớp học | - |
| 7 | `class_students` | Liên kết Lớp-Học sinh | - |
| 8 | `lessons` | Bài giảng/Giáo án | - |
| 9 | `quizzes` | Bài kiểm tra | - |
| 10 | `questions` | Câu hỏi | - |
| 11 | `answers` | Đáp án | - |
| 12 | `quiz_attempts` | Lượt làm bài | - |
| 13 | `student_answers` | Câu trả lời HS | - |
| 14 | `rubrics` | Rubric chấm tự luận | - |
| 15 | `essay_submissions` | Bài tự luận + AI feedback | - |
| 16 | `flashcard_sets` | Bộ flashcard | - |
| 17 | `flashcards` | Thẻ flashcard | - |
| 18 | `flashcard_reviews` | Lịch sử ôn tập (SRS) | - |
| 19 | `class_assignments` | Giao bài (lesson/quiz → class) | - |
| 20 | `ai_prompts` | AI Persona configs | Raina, Tutor, StudyBot |
| 21 | `documents` | Tài liệu upload (RAG) | - |
| 22 | `document_chunks` | Vector chunks (pgvector) | - |
| 23 | `chat_sessions` | Phiên chat AI | - |
| 24 | `chat_messages` | Tin nhắn chat | - |
| 25 | `ai_tasks` | Background AI tasks (Celery) | - |
| 26 | `generated_assets` | Asset AI đã sinh | - |

## Đặc điểm kỹ thuật

- **pgvector extension**: HNSW Index trên `document_chunks.embedding` (vector(1536))
- **Soft Delete**: `deleted_at` trên users, classes, lessons, quizzes, flashcard_sets, rubrics, documents
- **UUID primary keys**: `gen_random_uuid()` cho tất cả bảng
- **Check constraints**: Enum validation ở DB level (role, status, provider, task_type)
- **Async migration**: Sử dụng `asyncpg` engine trong `env.py`

## Commands

```bash
# Từ thư mục backend/

# Apply tất cả migrations
alembic upgrade head

# Rollback 1 migration
alembic downgrade -1

# Rollback toàn bộ
alembic downgrade base

# Tạo migration mới (autogenerate từ models)
alembic revision --autogenerate -m "description"

# Xem migration hiện tại
alembic current

# Xem lịch sử migration
alembic history --verbose

# Seed demo data (sau khi upgrade head)
python scripts/seed_demo_data.py
```

## Lưu ý quan trọng

1. **KHÔNG sửa migration cũ** — Luôn tạo migration mới để fix
2. **Import models** — Mọi model mới phải được import trong `app/domain/models/__init__.py`
3. **DATABASE_URL** — Load từ `app.core.config.settings`, KHÔNG hardcode trong `alembic.ini`
4. **pgvector** — Extension phải được enable trước khi chạy migration (xem `scripts/init-db.sh`)
