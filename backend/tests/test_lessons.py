"""
Test suite cho Lesson Module — Repository + UseCase + Router.
Dung function-scope fixtures tu conftest.py.

Test Strategy:
  - Tao teacher + student user fixtures
  - Test toan bo CRUD flow cho Lesson
  - Test authorization (teacher ownership, role checks)
  - Test validation (empty title, empty PATCH body)
"""
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.user import User, Profile
from app.core.security import hash_password, create_access_token


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────
async def _create_user(
    db: AsyncSession,
    username: str,
    email: str,
    role: str = "student",
) -> User:
    """Helper: Tao User + Profile truc tiep vao DB."""
    user = User(
        username=username,
        email=email,
        password_hash=hash_password("password123"),
        role=role,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    profile = Profile(user_id=user.id)
    db.add(profile)
    await db.flush()
    await db.refresh(user)
    return user


def _auth_headers(user: User) -> dict:
    """Tao Bearer token header cho user."""
    token = create_access_token(str(user.id), user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def teacher(db_session: AsyncSession) -> User:
    """Giao vien test."""
    return await _create_user(
        db_session,
        username="lesson_teacher",
        email="lesson_teacher@test.com",
        role="teacher",
    )


@pytest_asyncio.fixture(scope="function")
async def other_teacher(db_session: AsyncSession) -> User:
    """Giao vien khac — de test ownership."""
    return await _create_user(
        db_session,
        username="lesson_other_teacher",
        email="lesson_other_teacher@test.com",
        role="teacher",
    )


@pytest_asyncio.fixture(scope="function")
async def student(db_session: AsyncSession) -> User:
    """Hoc sinh test."""
    return await _create_user(
        db_session,
        username="lesson_student",
        email="lesson_student@test.com",
        role="student",
    )


# ──────────────────────────────────────────────
# Test: Create Lesson
# ──────────────────────────────────────────────
async def test_create_lesson_success(client: AsyncClient, teacher: User):
    """Teacher tao bai giang thanh cong."""
    response = await client.post(
        "/api/v1/lessons",
        json={
            "title": "Bai 1: Gioi thieu Python",
            "subject": "Tin Hoc",
            "grade_level": "10",
            "content": {"sections": [{"title": "Hello World"}]},
        },
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["title"] == "Bai 1: Gioi thieu Python"
    assert data["data"]["subject"] == "Tin Hoc"
    assert data["data"]["grade_level"] == "10"
    assert data["data"]["teacher_id"] == str(teacher.id)
    assert data["data"]["content"] == {"sections": [{"title": "Hello World"}]}
    # Fix #2 verification: teacher_name must be populated after create
    assert data["data"]["teacher_name"] == teacher.username


async def test_create_lesson_minimal(client: AsyncClient, teacher: User):
    """Tao bai giang chi voi title (subject, grade_level, content optional)."""
    response = await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang don gian"},
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["title"] == "Bai giang don gian"
    assert data["subject"] is None
    assert data["grade_level"] is None
    assert data["content"] is None


async def test_create_lesson_unauthorized(client: AsyncClient, student: User):
    """Student khong duoc tao bai giang (403 Forbidden)."""
    response = await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang khong hop le"},
        headers=_auth_headers(student),
    )
    assert response.status_code == 403


async def test_create_lesson_no_auth(client: AsyncClient):
    """Khong co token -> 401."""
    response = await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang Test"},
    )
    assert response.status_code == 401


async def test_create_lesson_empty_title(client: AsyncClient, teacher: User):
    """Title trong -> 422 Validation Error."""
    response = await client.post(
        "/api/v1/lessons",
        json={"title": "   "},
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 422


# ──────────────────────────────────────────────
# Test: List Lessons
# ──────────────────────────────────────────────
async def test_list_lessons_empty(client: AsyncClient, teacher: User):
    """Teacher chua co bai giang nao -> tra ve list rong."""
    response = await client.get(
        "/api/v1/lessons",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []


async def test_list_lessons_returns_own_lessons(
    client: AsyncClient,
    teacher: User,
    other_teacher: User,
):
    """Teacher chi thay bai giang cua minh, khong thay cua giao vien khac."""
    # Tao bai giang cho teacher
    await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang cua Teacher A"},
        headers=_auth_headers(teacher),
    )
    # Tao bai giang cho other_teacher
    await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang cua Teacher B"},
        headers=_auth_headers(other_teacher),
    )

    response = await client.get(
        "/api/v1/lessons",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 200
    lessons = response.json()["data"]
    assert len(lessons) == 1
    assert lessons[0]["title"] == "Bai giang cua Teacher A"


# ──────────────────────────────────────────────
# Test: Get Lesson Detail
# ──────────────────────────────────────────────
async def test_get_lesson_detail(client: AsyncClient, teacher: User):
    """Lay chi tiet bai giang."""
    create_resp = await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang Chi Tiet", "subject": "Toan"},
        headers=_auth_headers(teacher),
    )
    lesson_id = create_resp.json()["data"]["id"]

    response = await client.get(
        f"/api/v1/lessons/{lesson_id}",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == lesson_id
    assert data["title"] == "Bai giang Chi Tiet"
    assert data["teacher_name"] == teacher.username


async def test_get_lesson_not_found(client: AsyncClient, teacher: User):
    """Bai giang khong ton tai -> 404."""
    fake_id = str(uuid.uuid4())
    response = await client.get(
        f"/api/v1/lessons/{fake_id}",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 404


async def test_student_can_get_lesson_detail(
    client: AsyncClient,
    teacher: User,
    student: User,
):
    """Student (CurrentUserDep) co the xem chi tiet bai giang."""
    create_resp = await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang Student Xem"},
        headers=_auth_headers(teacher),
    )
    lesson_id = create_resp.json()["data"]["id"]

    response = await client.get(
        f"/api/v1/lessons/{lesson_id}",
        headers=_auth_headers(student),
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == lesson_id


# ──────────────────────────────────────────────
# Test: Update Lesson
# ──────────────────────────────────────────────
async def test_update_lesson_success(client: AsyncClient, teacher: User):
    """Teacher cap nhat bai giang cua minh thanh cong."""
    create_resp = await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang Cu"},
        headers=_auth_headers(teacher),
    )
    lesson_id = create_resp.json()["data"]["id"]

    response = await client.patch(
        f"/api/v1/lessons/{lesson_id}",
        json={"title": "Bai giang Moi", "subject": "Hoa"},
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "Bai giang Moi"
    assert data["subject"] == "Hoa"


async def test_update_lesson_forbidden(
    client: AsyncClient,
    teacher: User,
    other_teacher: User,
):
    """Teacher khong duoc sua bai giang cua teacher khac."""
    # teacher tao bai giang
    create_resp = await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang cua A"},
        headers=_auth_headers(teacher),
    )
    lesson_id = create_resp.json()["data"]["id"]

    # other_teacher co sua bai giang do
    response = await client.patch(
        f"/api/v1/lessons/{lesson_id}",
        json={"title": "Hacked"},
        headers=_auth_headers(other_teacher),
    )
    assert response.status_code == 403


async def test_update_lesson_empty_body(client: AsyncClient, teacher: User):
    """PATCH voi body rong (tat ca None) -> 422 Validation Error."""
    create_resp = await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang Test Empty PATCH"},
        headers=_auth_headers(teacher),
    )
    lesson_id = create_resp.json()["data"]["id"]

    response = await client.patch(
        f"/api/v1/lessons/{lesson_id}",
        json={},
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 422


async def test_update_lesson_all_null_fields(client: AsyncClient, teacher: User):
    """PATCH voi tat ca field = null -> 422 (regression guard)."""
    create_resp = await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang Test Null Fields"},
        headers=_auth_headers(teacher),
    )
    lesson_id = create_resp.json()["data"]["id"]

    response = await client.patch(
        f"/api/v1/lessons/{lesson_id}",
        json={"title": None},
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 422


# ──────────────────────────────────────────────
# Test: Delete Lesson
# ──────────────────────────────────────────────
async def test_delete_lesson_success(client: AsyncClient, teacher: User):
    """Teacher soft delete bai giang cua minh."""
    create_resp = await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang Can Xoa"},
        headers=_auth_headers(teacher),
    )
    lesson_id = create_resp.json()["data"]["id"]

    response = await client.delete(
        f"/api/v1/lessons/{lesson_id}",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 200

    # Verify bai giang khong con tim thay
    get_resp = await client.get(
        f"/api/v1/lessons/{lesson_id}",
        headers=_auth_headers(teacher),
    )
    assert get_resp.status_code == 404


async def test_delete_lesson_forbidden(
    client: AsyncClient,
    teacher: User,
    other_teacher: User,
):
    """Teacher khong duoc xoa bai giang cua teacher khac."""
    create_resp = await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang cua A"},
        headers=_auth_headers(teacher),
    )
    lesson_id = create_resp.json()["data"]["id"]

    response = await client.delete(
        f"/api/v1/lessons/{lesson_id}",
        headers=_auth_headers(other_teacher),
    )
    assert response.status_code == 403


async def test_delete_lesson_not_found(client: AsyncClient, teacher: User):
    """Xoa bai giang khong ton tai -> 404."""
    fake_id = str(uuid.uuid4())
    response = await client.delete(
        f"/api/v1/lessons/{fake_id}",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 404


# ──────────────────────────────────────────────
# Test: JSONB Content
# ──────────────────────────────────────────────
async def test_lesson_content_jsonb(client: AsyncClient, teacher: User):
    """Content field luu va tra ve JSONB dung cau truc."""
    content = {
        "sections": [
            {"title": "Gioi thieu", "body": "Noi dung gioi thieu"},
            {"title": "Bai tap", "body": "Lam bai tap 1-5"},
        ],
        "objectives": ["Hieu khai niem co ban", "Ap dung vao thuc te"],
    }
    create_resp = await client.post(
        "/api/v1/lessons",
        json={"title": "Bai giang JSONB", "content": content},
        headers=_auth_headers(teacher),
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["data"]["content"] == content

    # Update content
    new_content = {"sections": [{"title": "Updated"}]}
    lesson_id = create_resp.json()["data"]["id"]
    update_resp = await client.patch(
        f"/api/v1/lessons/{lesson_id}",
        json={"content": new_content},
        headers=_auth_headers(teacher),
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["content"] == new_content
