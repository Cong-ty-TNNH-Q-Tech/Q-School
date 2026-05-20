"""
Test suite cho Class Module — Repository + UseCase + Router.
Dùng function-scope fixtures từ conftest.py.

Test Strategy:
  - Tạo teacher + student user fixtures
  - Test toàn bộ CRUD flow cho Class
  - Test enrollment flow (enroll, remove, list students)
  - Test authorization (teacher ownership, role checks)
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
    """Helper: Tạo User + Profile trực tiếp vào DB."""
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
    """Tạo Bearer token header cho user."""
    token = create_access_token(str(user.id), user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def teacher(db_session: AsyncSession) -> User:
    """Giáo viên test."""
    return await _create_user(
        db_session,
        username="teacher_test",
        email="teacher@test.com",
        role="teacher",
    )


@pytest_asyncio.fixture(scope="function")
async def other_teacher(db_session: AsyncSession) -> User:
    """Giáo viên khác — để test ownership."""
    return await _create_user(
        db_session,
        username="other_teacher",
        email="other_teacher@test.com",
        role="teacher",
    )


@pytest_asyncio.fixture(scope="function")
async def student(db_session: AsyncSession) -> User:
    """Học sinh test."""
    return await _create_user(
        db_session,
        username="student_test",
        email="student@test.com",
        role="student",
    )


# ──────────────────────────────────────────────
# Test: Create Class
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_create_class_success(client: AsyncClient, teacher: User):
    """Teacher tạo lớp học thành công."""
    response = await client.post(
        "/api/v1/classes",
        json={
            "name": "Lớp Toán 10A",
            "grade_level": "10",
            "subject": "Toán",
        },
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["name"] == "Lớp Toán 10A"
    assert data["data"]["grade_level"] == "10"
    assert data["data"]["subject"] == "Toán"
    assert data["data"]["teacher_id"] == str(teacher.id)
    assert data["data"]["student_count"] == 0


@pytest.mark.asyncio
async def test_create_class_minimal(client: AsyncClient, teacher: User):
    """Tạo lớp với chỉ tên (grade_level, subject optional)."""
    response = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp Văn"},
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "Lớp Văn"
    assert data["grade_level"] is None
    assert data["subject"] is None


@pytest.mark.asyncio
async def test_create_class_unauthorized(client: AsyncClient, student: User):
    """Student không được tạo lớp (403 Forbidden)."""
    response = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp Không Hợp Lệ"},
        headers=_auth_headers(student),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_class_no_auth(client: AsyncClient):
    """Không có token → 401."""
    response = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp Test"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_class_empty_name(client: AsyncClient, teacher: User):
    """Tên lớp trống → 422 Validation Error."""
    response = await client.post(
        "/api/v1/classes",
        json={"name": "   "},
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 422


# ──────────────────────────────────────────────
# Test: List Classes
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_list_classes_empty(client: AsyncClient, teacher: User):
    """Teacher chưa có lớp nào → trả về list rỗng."""
    response = await client.get(
        "/api/v1/classes",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []


@pytest.mark.asyncio
async def test_list_classes_returns_own_classes(
    client: AsyncClient,
    teacher: User,
    other_teacher: User,
):
    """Teacher chỉ thấy lớp của mình, không thấy lớp của giáo viên khác."""
    # Tạo lớp cho teacher
    await client.post(
        "/api/v1/classes",
        json={"name": "Lớp của Teacher A"},
        headers=_auth_headers(teacher),
    )
    # Tạo lớp cho other_teacher
    await client.post(
        "/api/v1/classes",
        json={"name": "Lớp của Teacher B"},
        headers=_auth_headers(other_teacher),
    )

    response = await client.get(
        "/api/v1/classes",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 200
    classes = response.json()["data"]
    assert len(classes) == 1
    assert classes[0]["name"] == "Lớp của Teacher A"


# ──────────────────────────────────────────────
# Test: Get Class Detail
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_class_detail(client: AsyncClient, teacher: User):
    """Lấy chi tiết lớp học."""
    create_resp = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp Lý 11B", "subject": "Vật Lý"},
        headers=_auth_headers(teacher),
    )
    class_id = create_resp.json()["data"]["id"]

    response = await client.get(
        f"/api/v1/classes/{class_id}",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == class_id
    assert data["name"] == "Lớp Lý 11B"
    assert data["students"] == []


@pytest.mark.asyncio
async def test_get_class_not_found(client: AsyncClient, teacher: User):
    """Lớp không tồn tại → 404."""
    fake_id = str(uuid.uuid4())
    response = await client.get(
        f"/api/v1/classes/{fake_id}",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 404


# ──────────────────────────────────────────────
# Test: Update Class
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_update_class_success(client: AsyncClient, teacher: User):
    """Teacher cập nhật lớp của mình thành công."""
    create_resp = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp Cũ"},
        headers=_auth_headers(teacher),
    )
    class_id = create_resp.json()["data"]["id"]

    response = await client.patch(
        f"/api/v1/classes/{class_id}",
        json={"name": "Lớp Mới", "subject": "Hóa"},
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "Lớp Mới"
    assert data["subject"] == "Hóa"


@pytest.mark.asyncio
async def test_update_class_forbidden(
    client: AsyncClient,
    teacher: User,
    other_teacher: User,
):
    """Teacher không được sửa lớp của teacher khác."""
    # teacher tạo lớp
    create_resp = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp của A"},
        headers=_auth_headers(teacher),
    )
    class_id = create_resp.json()["data"]["id"]

    # other_teacher cố sửa lớp đó
    response = await client.patch(
        f"/api/v1/classes/{class_id}",
        json={"name": "Hacked"},
        headers=_auth_headers(other_teacher),
    )
    assert response.status_code == 403


# ──────────────────────────────────────────────
# Test: Delete Class
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_delete_class_success(client: AsyncClient, teacher: User):
    """Teacher soft delete lớp của mình."""
    create_resp = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp Cần Xóa"},
        headers=_auth_headers(teacher),
    )
    class_id = create_resp.json()["data"]["id"]

    response = await client.delete(
        f"/api/v1/classes/{class_id}",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 200

    # Verify lớp không còn tìm thấy
    get_resp = await client.get(
        f"/api/v1/classes/{class_id}",
        headers=_auth_headers(teacher),
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_class_forbidden(
    client: AsyncClient,
    teacher: User,
    other_teacher: User,
):
    """Teacher không được xóa lớp của teacher khác."""
    create_resp = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp của A"},
        headers=_auth_headers(teacher),
    )
    class_id = create_resp.json()["data"]["id"]

    response = await client.delete(
        f"/api/v1/classes/{class_id}",
        headers=_auth_headers(other_teacher),
    )
    assert response.status_code == 403


# ──────────────────────────────────────────────
# Test: Student Enrollment
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_enroll_student_success(
    client: AsyncClient,
    teacher: User,
    student: User,
):
    """Teacher thêm học sinh vào lớp thành công."""
    create_resp = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp Enrollment Test"},
        headers=_auth_headers(teacher),
    )
    class_id = create_resp.json()["data"]["id"]

    response = await client.post(
        f"/api/v1/classes/{class_id}/students",
        json={"student_id": str(student.id)},
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["student_id"] == str(student.id)


@pytest.mark.asyncio
async def test_enroll_student_duplicate(
    client: AsyncClient,
    teacher: User,
    student: User,
):
    """Thêm học sinh đã có trong lớp → 409 Conflict."""
    create_resp = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp Duplicate Test"},
        headers=_auth_headers(teacher),
    )
    class_id = create_resp.json()["data"]["id"]

    # Thêm lần 1
    await client.post(
        f"/api/v1/classes/{class_id}/students",
        json={"student_id": str(student.id)},
        headers=_auth_headers(teacher),
    )

    # Thêm lần 2 → phải conflict
    response = await client.post(
        f"/api/v1/classes/{class_id}/students",
        json={"student_id": str(student.id)},
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_students(
    client: AsyncClient,
    teacher: User,
    student: User,
):
    """Lấy danh sách học sinh trong lớp."""
    create_resp = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp List Students Test"},
        headers=_auth_headers(teacher),
    )
    class_id = create_resp.json()["data"]["id"]

    await client.post(
        f"/api/v1/classes/{class_id}/students",
        json={"student_id": str(student.id)},
        headers=_auth_headers(teacher),
    )

    response = await client.get(
        f"/api/v1/classes/{class_id}/students",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 200
    students = response.json()["data"]
    assert len(students) == 1
    assert students[0]["student_id"] == str(student.id)


@pytest.mark.asyncio
async def test_remove_student_success(
    client: AsyncClient,
    teacher: User,
    student: User,
):
    """Teacher xóa học sinh khỏi lớp thành công."""
    create_resp = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp Remove Test"},
        headers=_auth_headers(teacher),
    )
    class_id = create_resp.json()["data"]["id"]

    # Enroll trước
    await client.post(
        f"/api/v1/classes/{class_id}/students",
        json={"student_id": str(student.id)},
        headers=_auth_headers(teacher),
    )

    # Remove
    response = await client.delete(
        f"/api/v1/classes/{class_id}/students/{student.id}",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 200

    # Verify
    list_resp = await client.get(
        f"/api/v1/classes/{class_id}/students",
        headers=_auth_headers(teacher),
    )
    assert list_resp.json()["data"] == []


@pytest.mark.asyncio
async def test_remove_student_not_enrolled(
    client: AsyncClient,
    teacher: User,
    student: User,
):
    """Xóa học sinh chưa trong lớp → 404."""
    create_resp = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp Remove Not Enrolled"},
        headers=_auth_headers(teacher),
    )
    class_id = create_resp.json()["data"]["id"]

    response = await client.delete(
        f"/api/v1/classes/{class_id}/students/{student.id}",
        headers=_auth_headers(teacher),
    )
    assert response.status_code == 404


# ──────────────────────────────────────────────
# Test: Student Validation (role + existence)
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_enroll_nonexistent_student(
    client: AsyncClient,
    teacher: User,
):
    """Enroll student_id không tồn tại trong DB → 404 (không được là 500 FK error)."""
    create_resp = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp Validate Test"},
        headers=_auth_headers(teacher),
    )
    class_id = create_resp.json()["data"]["id"]

    fake_student_id = str(uuid.uuid4())
    response = await client.post(
        f"/api/v1/classes/{class_id}/students",
        json={"student_id": fake_student_id},
        headers=_auth_headers(teacher),
    )
    # Phải là 404, KHÔNG phải 500 (FK IntegrityError)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_enroll_teacher_as_student_rejected(
    client: AsyncClient,
    teacher: User,
    other_teacher: User,
):
    """Không thể enroll một giáo viên khác vào lớp với tư cách 'học sinh'."""
    create_resp = await client.post(
        "/api/v1/classes",
        json={"name": "Lớp Role Check Test"},
        headers=_auth_headers(teacher),
    )
    class_id = create_resp.json()["data"]["id"]

    response = await client.post(
        f"/api/v1/classes/{class_id}/students",
        json={"student_id": str(other_teacher.id)},
        headers=_auth_headers(teacher),
    )
    # Teacher không phải student → 404 (UserNotFoundError)
    assert response.status_code == 404
