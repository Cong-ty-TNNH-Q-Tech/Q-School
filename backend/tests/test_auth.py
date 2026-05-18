"""
Integration Tests — Auth API Endpoints.
Đây là PATTERN MẪU cho các test khác.

Test Isolation: SAVEPOINT-based (xem conftest.py).
Mỗi test tự rollback — không cần cleanup thủ công.

Member: Copy pattern này khi viết test cho classes, quizzes...
"""
import pytest
from httpx import AsyncClient


# ──────────────────────────────────────────────
# Helpers / Fixtures
# ──────────────────────────────────────────────
REGISTER_PAYLOAD = {
    "username": "testuser",
    "email": "test@qschool.vn",
    "password": "password123",
    "role": "student",
}

TEACHER_PAYLOAD = {
    "username": "testteacher",
    "email": "teacher@qschool.vn",
    "password": "password123",
    "role": "teacher",
}


async def _register_and_login(client: AsyncClient, payload: dict) -> dict:
    """Helper: đăng ký + lấy token, dùng lại trong nhiều tests."""
    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201, f"Register failed: {res.text}"
    return res.json()["data"]["tokens"]


# ──────────────────────────────────────────────
# POST /auth/register
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Đăng ký thành công → 201 + trả về tokens và user info."""
    res = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "success"
    assert "access_token" in body["data"]["tokens"]
    assert "refresh_token" in body["data"]["tokens"]
    assert body["data"]["user"]["email"] == REGISTER_PAYLOAD["email"]
    assert body["data"]["user"]["role"] == "student"
    # Không bao giờ trả về password_hash
    assert "password_hash" not in body["data"]["user"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Đăng ký email trùng → 409 Conflict."""
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    res = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

    assert res.status_code == 409
    assert res.json()["error_code"] == 4090


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    """Đăng ký username trùng, email khác → 409 Conflict."""
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    new_payload = {**REGISTER_PAYLOAD, "email": "another@qschool.vn"}
    res = await client.post("/api/v1/auth/register", json=new_payload)

    assert res.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_role(client: AsyncClient):
    """Role không hợp lệ → 422 Validation Error."""
    payload = {**REGISTER_PAYLOAD, "role": "admin"}  # Admin không thể tự đăng ký
    res = await client.post("/api/v1/auth/register", json=payload)

    assert res.status_code == 422
    assert res.json()["error_code"] == 4220


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Password dưới 6 ký tự → 422."""
    payload = {**REGISTER_PAYLOAD, "password": "123"}
    res = await client.post("/api/v1/auth/register", json=payload)

    assert res.status_code == 422


@pytest.mark.asyncio
async def test_register_teacher_role(client: AsyncClient):
    """Giáo viên đăng ký được với role='teacher'."""
    res = await client.post("/api/v1/auth/register", json=TEACHER_PAYLOAD)

    assert res.status_code == 201
    assert res.json()["data"]["user"]["role"] == "teacher"


# ──────────────────────────────────────────────
# POST /auth/login
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_login_success_by_username(client: AsyncClient):
    """Đăng nhập bằng username → 200 + tokens."""
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

    res = await client.post(
        "/api/v1/auth/login",
        json={"username": REGISTER_PAYLOAD["username"], "password": REGISTER_PAYLOAD["password"]},
    )

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert body["data"]["tokens"]["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_success_by_email(client: AsyncClient):
    """Đăng nhập bằng email → 200 + tokens."""
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

    res = await client.post(
        "/api/v1/auth/login",
        json={"username": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )

    assert res.status_code == 200


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Sai mật khẩu → 401, KHÔNG tiết lộ user tồn tại hay không."""
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

    res = await client.post(
        "/api/v1/auth/login",
        json={"username": REGISTER_PAYLOAD["username"], "password": "wrongpass"},
    )

    assert res.status_code == 401
    assert res.json()["error_code"] == 4010


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """User không tồn tại → 401 (cùng error với sai password — tránh user enumeration)."""
    res = await client.post(
        "/api/v1/auth/login",
        json={"username": "nobody", "password": "anypass"},
    )

    assert res.status_code == 401
    assert res.json()["error_code"] == 4010


# ──────────────────────────────────────────────
# POST /auth/refresh
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient):
    """Refresh token hợp lệ → access_token mới."""
    tokens = await _register_and_login(client, REGISTER_PAYLOAD)
    refresh_token = tokens["refresh_token"]

    res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

    assert res.status_code == 200
    assert "access_token" in res.json()["data"]


@pytest.mark.asyncio
async def test_refresh_with_access_token_fails(client: AsyncClient):
    """Dùng access_token để refresh → 401 (sai token type)."""
    tokens = await _register_and_login(client, REGISTER_PAYLOAD)
    access_token = tokens["access_token"]

    res = await client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})

    assert res.status_code == 401


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """Token giả → 401."""
    res = await client.post("/api/v1/auth/refresh", json={"refresh_token": "totally.fake.token"})

    assert res.status_code == 401


# ──────────────────────────────────────────────
# GET /auth/me
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_me_success(client: AsyncClient):
    """GET /auth/me với Bearer token hợp lệ → trả về user info."""
    tokens = await _register_and_login(client, REGISTER_PAYLOAD)
    access_token = tokens["access_token"]

    res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert res.status_code == 200
    body = res.json()
    assert body["data"]["email"] == REGISTER_PAYLOAD["email"]
    assert "password_hash" not in body["data"]


@pytest.mark.asyncio
async def test_get_me_without_token(client: AsyncClient):
    """GET /auth/me không có token → 401."""
    res = await client.get("/api/v1/auth/me")

    assert res.status_code == 401
    assert res.json()["error_code"] == 4010


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    """GET /auth/me với token giả → 401."""
    res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer fake.token.here"},
    )

    assert res.status_code == 401


# ──────────────────────────────────────────────
# POST /auth/logout
# ──────────────────────────────────────────────
@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient):
    """Logout với valid token → 200."""
    tokens = await _register_and_login(client, REGISTER_PAYLOAD)

    res = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert res.status_code == 200
    assert res.json()["status"] == "success"


@pytest.mark.asyncio
async def test_register_username_with_special_chars_rejected(client: AsyncClient):
    """Username chứa ký tự đặc biệt → 422 Validation Error."""
    for bad_username in ["user name", "user@name", "user<script>", "user;drop"]:
        payload = {**REGISTER_PAYLOAD, "username": bad_username}
        res = await client.post("/api/v1/auth/register", json=payload)
        assert res.status_code == 422, f"Expected 422 for username: {bad_username!r}"


@pytest.mark.asyncio
async def test_login_email_case_insensitive(client: AsyncClient):
    """Đăng nhập bằng email chữ hoa → vẫn tìm được user (normalize lowercase)."""
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

    res = await client.post(
        "/api/v1/auth/login",
        json={
            "username": REGISTER_PAYLOAD["email"].upper(),  # TEST@QSCHOOL.VN
            "password": REGISTER_PAYLOAD["password"],
        },
    )

    assert res.status_code == 200, "Email login phải case-insensitive"


@pytest.mark.asyncio
async def test_token_valid_after_logout_known_limitation(client: AsyncClient):
    """
    KNOWN LIMITATION: Token vẫn còn hiệu lực sau khi logout (stateless JWT, chưa có Redis blacklist).

    Test này DOCUMENT current behavior, KHÔNG phải lỗi.
    Khi Redis token blacklist được implement:
      - test này SẼ FAIL (expected 401, got 200)
      - Đó là dấu hiệu để UPDATE assert thành 401
    TODO: implement Redis blacklist trong POST /auth/logout
    """
    tokens = await _register_and_login(client, REGISTER_PAYLOAD)
    access_token = tokens["access_token"]

    # Logout
    await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Token cũ vẫn hoạt động — KNOWN LIMITATION
    res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert res.status_code == 200, (
        "EXPECTED: Token vẫn valid sau logout (stateless JWT). "
        "Nếu test này fail với 401, Redis blacklist đã được implement — cập nhật assert!"
    )
