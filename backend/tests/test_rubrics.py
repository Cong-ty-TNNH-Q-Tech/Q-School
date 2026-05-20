"""
Integration Tests — Rubric CRUD API Endpoints.
Pattern copy từ test_auth.py.

Test Isolation: SAVEPOINT-based (xem conftest.py).
Mỗi test tự rollback — không cần cleanup thủ công.
"""
import uuid

import pytest
from httpx import AsyncClient


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
TEACHER_PAYLOAD = {
    "username": "rubric_teacher",
    "email": "rubric_teacher@qschool.vn",
    "password": "password123",
    "role": "teacher",
}

TEACHER2_PAYLOAD = {
    "username": "rubric_teacher2",
    "email": "rubric_teacher2@qschool.vn",
    "password": "password123",
    "role": "teacher",
}

STUDENT_PAYLOAD = {
    "username": "rubric_student",
    "email": "rubric_student@qschool.vn",
    "password": "password123",
    "role": "student",
}

SAMPLE_RUBRIC = {
    "title": "Writing Assessment Rubric",
    "criteria_matrix": {
        "content": {"excellent": 5, "good": 4, "fair": 3, "poor": 1},
        "grammar": {"excellent": 5, "good": 4, "fair": 3, "poor": 1},
        "structure": {"excellent": 5, "good": 4, "fair": 3, "poor": 1},
    },
}


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def register_teacher(client: AsyncClient, payload: dict = None) -> str:
    """Đăng ký teacher, trả về access_token."""
    payload = payload or TEACHER_PAYLOAD
    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201, f"Register teacher failed: {res.text}"
    return res.json()["data"]["tokens"]["access_token"]


async def register_student(client: AsyncClient) -> str:
    """Đăng ký student, trả về access_token."""
    res = await client.post("/api/v1/auth/register", json=STUDENT_PAYLOAD)
    assert res.status_code == 201, f"Register student failed: {res.text}"
    return res.json()["data"]["tokens"]["access_token"]


async def create_rubric(client: AsyncClient, token: str, data: dict = None) -> dict:
    """Tạo rubric mẫu, trả về rubric data."""
    data = data or SAMPLE_RUBRIC
    res = await client.post(
        "/api/v1/rubrics", json=data, headers=auth_header(token)
    )
    assert res.status_code == 201, f"Create rubric failed: {res.text}"
    return res.json()["data"]


# ──────────────────────────────────────────────
# POST /rubrics
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_create_rubric_success(client: AsyncClient):
    """Tạo rubric thành công → 201 + trả về RubricOut."""
    token = await register_teacher(client)
    res = await client.post(
        "/api/v1/rubrics", json=SAMPLE_RUBRIC, headers=auth_header(token)
    )

    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "success"
    assert body["message"] == "Tạo rubric thành công"
    data = body["data"]
    assert data["title"] == SAMPLE_RUBRIC["title"]
    assert data["criteria_matrix"] == SAMPLE_RUBRIC["criteria_matrix"]
    assert "id" in data
    assert "teacher_id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_rubric_empty_title(client: AsyncClient):
    """Title rỗng → 422 validation error."""
    token = await register_teacher(client)
    payload = {"title": "   ", "criteria_matrix": {"a": 1}}
    res = await client.post(
        "/api/v1/rubrics", json=payload, headers=auth_header(token)
    )

    assert res.status_code == 422


@pytest.mark.asyncio
async def test_create_rubric_empty_matrix(client: AsyncClient):
    """criteria_matrix rỗng → 422 validation error."""
    token = await register_teacher(client)
    payload = {"title": "Valid Title", "criteria_matrix": {}}
    res = await client.post(
        "/api/v1/rubrics", json=payload, headers=auth_header(token)
    )

    assert res.status_code == 422


@pytest.mark.asyncio
async def test_create_rubric_student_forbidden(client: AsyncClient):
    """Student tạo rubric → 403."""
    token = await register_student(client)
    res = await client.post(
        "/api/v1/rubrics", json=SAMPLE_RUBRIC, headers=auth_header(token)
    )

    assert res.status_code == 403


@pytest.mark.asyncio
async def test_create_rubric_no_auth(client: AsyncClient):
    """Không có token → 401."""
    res = await client.post("/api/v1/rubrics", json=SAMPLE_RUBRIC)

    assert res.status_code == 401


# ──────────────────────────────────────────────
# GET /rubrics (list)
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_list_rubrics_success(client: AsyncClient):
    """Liệt kê rubrics của teacher → 200 + list."""
    token = await register_teacher(client)
    await create_rubric(client, token)
    await create_rubric(client, token, {
        "title": "Second Rubric",
        "criteria_matrix": {"x": 1},
    })

    res = await client.get("/api/v1/rubrics", headers=auth_header(token))

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert len(body["data"]) == 2


@pytest.mark.asyncio
async def test_list_rubrics_empty(client: AsyncClient):
    """Teacher chưa có rubric → 200 + []."""
    token = await register_teacher(client)

    res = await client.get("/api/v1/rubrics", headers=auth_header(token))

    assert res.status_code == 200
    assert res.json()["data"] == []


# ──────────────────────────────────────────────
# GET /rubrics/{id}
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_rubric_success(client: AsyncClient):
    """Lấy chi tiết rubric → 200."""
    token = await register_teacher(client)
    rubric = await create_rubric(client, token)

    res = await client.get(
        f"/api/v1/rubrics/{rubric['id']}", headers=auth_header(token)
    )

    assert res.status_code == 200
    assert res.json()["data"]["id"] == rubric["id"]
    assert res.json()["data"]["title"] == SAMPLE_RUBRIC["title"]


@pytest.mark.asyncio
async def test_get_rubric_not_found(client: AsyncClient):
    """ID không tồn tại → 404."""
    token = await register_teacher(client)
    fake_id = str(uuid.uuid4())

    res = await client.get(
        f"/api/v1/rubrics/{fake_id}", headers=auth_header(token)
    )

    assert res.status_code == 404


@pytest.mark.asyncio
async def test_get_rubric_other_teacher(client: AsyncClient):
    """Teacher khác truy cập rubric → 404 (không leak info)."""
    token1 = await register_teacher(client, TEACHER_PAYLOAD)
    rubric = await create_rubric(client, token1)

    token2 = await register_teacher(client, TEACHER2_PAYLOAD)
    res = await client.get(
        f"/api/v1/rubrics/{rubric['id']}", headers=auth_header(token2)
    )

    assert res.status_code == 404


@pytest.mark.asyncio
async def test_get_rubric_student_not_owner(client: AsyncClient):
    """Student truy cập rubric → 404 (ownership check, không phải 403)."""
    teacher_token = await register_teacher(client)
    rubric = await create_rubric(client, teacher_token)

    student_token = await register_student(client)
    res = await client.get(
        f"/api/v1/rubrics/{rubric['id']}", headers=auth_header(student_token)
    )

    assert res.status_code == 404


# ──────────────────────────────────────────────
# PATCH /rubrics/{id}
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_update_rubric_title(client: AsyncClient):
    """Cập nhật title → 200 + title đã đổi."""
    token = await register_teacher(client)
    rubric = await create_rubric(client, token)

    res = await client.patch(
        f"/api/v1/rubrics/{rubric['id']}",
        json={"title": "Updated Title"},
        headers=auth_header(token),
    )

    assert res.status_code == 200
    assert res.json()["data"]["title"] == "Updated Title"
    assert res.json()["data"]["criteria_matrix"] == SAMPLE_RUBRIC["criteria_matrix"]


@pytest.mark.asyncio
async def test_update_rubric_matrix(client: AsyncClient):
    """Cập nhật criteria_matrix → 200."""
    token = await register_teacher(client)
    rubric = await create_rubric(client, token)
    new_matrix = {"new_criteria": {"level1": 10, "level2": 5}}

    res = await client.patch(
        f"/api/v1/rubrics/{rubric['id']}",
        json={"criteria_matrix": new_matrix},
        headers=auth_header(token),
    )

    assert res.status_code == 200
    assert res.json()["data"]["criteria_matrix"] == new_matrix
    assert res.json()["data"]["title"] == SAMPLE_RUBRIC["title"]


@pytest.mark.asyncio
async def test_update_rubric_not_found(client: AsyncClient):
    """Update rubric không tồn tại → 404."""
    token = await register_teacher(client)
    fake_id = str(uuid.uuid4())

    res = await client.patch(
        f"/api/v1/rubrics/{fake_id}",
        json={"title": "New Title"},
        headers=auth_header(token),
    )

    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_rubric_empty_body(client: AsyncClient):
    """Update body rỗng → 422 validation error."""
    token = await register_teacher(client)
    rubric = await create_rubric(client, token)

    res = await client.patch(
        f"/api/v1/rubrics/{rubric['id']}",
        json={},
        headers=auth_header(token),
    )

    assert res.status_code == 422


# ──────────────────────────────────────────────
# DELETE /rubrics/{id}
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_delete_rubric_success(client: AsyncClient):
    """Soft delete rubric → 200."""
    token = await register_teacher(client)
    rubric = await create_rubric(client, token)

    res = await client.delete(
        f"/api/v1/rubrics/{rubric['id']}", headers=auth_header(token)
    )

    assert res.status_code == 200
    assert res.json()["message"] == "Xóa rubric thành công"


@pytest.mark.asyncio
async def test_delete_rubric_not_found(client: AsyncClient):
    """Delete rubric không tồn tại → 404."""
    token = await register_teacher(client)
    fake_id = str(uuid.uuid4())

    res = await client.delete(
        f"/api/v1/rubrics/{fake_id}", headers=auth_header(token)
    )

    assert res.status_code == 404


@pytest.mark.asyncio
async def test_get_deleted_rubric(client: AsyncClient):
    """Rubric đã soft-delete → GET trả về 404."""
    token = await register_teacher(client)
    rubric = await create_rubric(client, token)

    # Soft delete
    await client.delete(
        f"/api/v1/rubrics/{rubric['id']}", headers=auth_header(token)
    )

    # GET should return 404
    res = await client.get(
        f"/api/v1/rubrics/{rubric['id']}", headers=auth_header(token)
    )

    assert res.status_code == 404
