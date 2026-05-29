"""
Tests cho Generated Assets Router.
Dùng local FastAPI app fixture — tách biệt với conftest.py (tránh DB connection).
Override require_active_subscription + get_use_case bằng mock.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.application.use_cases.generated_asset_use_case import (
    GeneratedAssetDTO,
    PaginatedAssetsDTO,
)
from app.core.dependencies import require_active_subscription, get_current_user, get_db
from app.entrypoints.api_v1.routers.generated_assets import get_use_case

# ── helpers ───────────────────────────────────────────────────────────────────

AI_USER = type(
    "User",
    (),
    {"id": uuid.uuid4(), "role": "teacher", "username": "aiteacher"},
)()


def _dto(
    asset_type: str = "email",
    creator_id: uuid.UUID | None = None,
) -> GeneratedAssetDTO:
    return GeneratedAssetDTO(
        id=uuid.uuid4(),
        creator_id=creator_id or AI_USER.id,
        asset_type=asset_type,
        input_params={"student_name": "Minh"},
        output_content={"content": "AI generated content"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


# ── App fixture ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def asset_app() -> FastAPI:
    """Lightweight test app cho Generated Assets — không có lifespan DB."""
    from app.entrypoints.api_v1.routers.generated_assets import router as assets_router
    from app.core.exceptions import register_exception_handlers

    app = FastAPI(title="Generated Asset Test App")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(assets_router, prefix="/api/v1/generated-assets")
    register_exception_handlers(app)  # 401/402/404/422 đúng status code
    return app


@pytest.fixture
def mock_uc() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def authed_client(asset_app: FastAPI, mock_uc: AsyncMock, monkeypatch) -> TestClient:
    """Client với AIUserDep + CurrentUserDep + UseCase đều bị mock."""
    asset_app.dependency_overrides[require_active_subscription] = lambda: AI_USER
    asset_app.dependency_overrides[get_current_user] = lambda: AI_USER
    asset_app.dependency_overrides[get_db] = lambda: AsyncMock()
    asset_app.dependency_overrides[get_use_case] = lambda: mock_uc
    
    # Mock celery task .delay to avoid hitting real Redis/Celery broker in router tests
    from app.entrypoints.celery_worker.ai_tasks import generate_asset_task
    monkeypatch.setattr(generate_asset_task, "delay", MagicMock())
    
    with TestClient(asset_app, raise_server_exceptions=True) as c:
        yield c
    asset_app.dependency_overrides.clear()



@pytest.fixture
def anon_client(asset_app: FastAPI) -> TestClient:
    """Client không có auth — test 401 (với raise_server_exceptions=False)."""
    asset_app.dependency_overrides.clear()
    with TestClient(asset_app, raise_server_exceptions=False) as c:
        yield c


# ── POST /generated-assets ────────────────────────────────────────────────────


class TestPostGeneratedAssets:
    def test_create_returns_202(self, authed_client: TestClient, mock_uc: AsyncMock):
        mock_uc.pre_create_asset.return_value = _dto("email")
        resp = authed_client.post(
            "/api/v1/generated-assets",
            json={"asset_type": "email", "input_params": {"student_name": "Minh"}},
        )
        assert resp.status_code == 202
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["asset_type"] == "email"

    def test_create_iep_returns_202(
        self, authed_client: TestClient, mock_uc: AsyncMock
    ):
        mock_uc.pre_create_asset.return_value = _dto("iep")
        resp = authed_client.post(
            "/api/v1/generated-assets",
            json={"asset_type": "iep", "input_params": {}},
        )
        assert resp.status_code == 202

    def test_create_missing_asset_type_returns_422(self, authed_client: TestClient):
        resp = authed_client.post(
            "/api/v1/generated-assets",
            json={"input_params": {}},
        )
        assert resp.status_code == 422

    def test_create_invalid_asset_type_returns_422(self, authed_client: TestClient):
        resp = authed_client.post(
            "/api/v1/generated-assets",
            json={"asset_type": "invalid_type", "input_params": {}},
        )
        assert resp.status_code == 422

    def test_create_without_auth_returns_401(self, anon_client: TestClient):
        resp = anon_client.post(
            "/api/v1/generated-assets",
            json={"asset_type": "email", "input_params": {}},
        )
        assert resp.status_code in (401, 402)

    def test_create_calls_use_case_with_correct_params(
        self, authed_client: TestClient, mock_uc: AsyncMock
    ):
        dto = _dto("behavior_intervention")
        mock_uc.pre_create_asset.return_value = dto
        authed_client.post(
            "/api/v1/generated-assets",
            json={
                "asset_type": "behavior_intervention",
                "input_params": {"student": "An", "behavior": "disruptive"},
            },
        )
        mock_uc.pre_create_asset.assert_called_once_with(
            creator_id=AI_USER.id,
            asset_type="behavior_intervention",
            input_params={"student": "An", "behavior": "disruptive"},
        )

    def test_create_empty_input_params_allowed(
        self, authed_client: TestClient, mock_uc: AsyncMock
    ):
        mock_uc.pre_create_asset.return_value = _dto("report_comment")
        resp = authed_client.post(
            "/api/v1/generated-assets",
            json={"asset_type": "report_comment"},
        )
        assert resp.status_code == 202

    def test_create_rate_limited_returns_429(
        self, authed_client: TestClient, monkeypatch
    ):
        from app.core.exceptions import TooManyRequestsException

        async def mock_check_rate_limit(*args, **kwargs):
            raise TooManyRequestsException("Rate limit exceeded")

        import app.entrypoints.api_v1.routers.generated_assets as router_module
        monkeypatch.setattr(router_module, "check_rate_limit", mock_check_rate_limit)

        resp = authed_client.post(
            "/api/v1/generated-assets",
            json={"asset_type": "email", "input_params": {"student_name": "Minh"}},
        )
        assert resp.status_code == 429
        assert resp.json()["error_code"] == 4290


# ── GET /generated-assets ─────────────────────────────────────────────────────


class TestGetListGeneratedAssets:
    def test_list_returns_200_with_data(
        self, authed_client: TestClient, mock_uc: AsyncMock
    ):
        dtos = [_dto("email"), _dto("iep")]
        mock_uc.list_assets.return_value = PaginatedAssetsDTO(
            items=dtos, has_more=False
        )
        resp = authed_client.get("/api/v1/generated-assets")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert len(body["data"]) == 2
        assert body["has_more"] is False

    def test_list_empty_returns_200(
        self, authed_client: TestClient, mock_uc: AsyncMock
    ):
        mock_uc.list_assets.return_value = PaginatedAssetsDTO(items=[], has_more=False)
        resp = authed_client.get("/api/v1/generated-assets")
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    def test_list_with_cursor_returns_200(
        self, authed_client: TestClient, mock_uc: AsyncMock
    ):
        now_iso = datetime.now(timezone.utc).isoformat()
        mock_uc.list_assets.return_value = PaginatedAssetsDTO(items=[], has_more=False)
        resp = authed_client.get(
            f"/api/v1/generated-assets?cursor_created_at={now_iso}&cursor_id={uuid.uuid4()}&limit=5"
        )
        assert resp.status_code == 200

    def test_list_has_more_returns_cursor(
        self, authed_client: TestClient, mock_uc: AsyncMock
    ):
        dtos = [_dto("email")]
        cursor_dt = datetime.now(timezone.utc).isoformat()
        cursor_id = str(uuid.uuid4())
        mock_uc.list_assets.return_value = PaginatedAssetsDTO(
            items=dtos,
            has_more=True,
            next_cursor_created_at=cursor_dt,
            next_cursor_id=cursor_id,
        )
        resp = authed_client.get("/api/v1/generated-assets")
        body = resp.json()
        assert body["has_more"] is True
        assert body["next_cursor_created_at"] == cursor_dt
        assert body["next_cursor_id"] == cursor_id

    def test_list_limit_exceeds_50_returns_422(self, authed_client: TestClient):
        resp = authed_client.get("/api/v1/generated-assets?limit=100")
        assert resp.status_code == 422

    def test_list_without_auth_returns_401(self, anon_client: TestClient):
        resp = anon_client.get("/api/v1/generated-assets")
        assert resp.status_code in (401, 402)


# ── GET /generated-assets/{id} ────────────────────────────────────────────────


class TestGetGeneratedAssetDetail:
    def test_get_returns_200(self, authed_client: TestClient, mock_uc: AsyncMock):
        dto = _dto("iep")
        mock_uc.get_asset.return_value = dto
        resp = authed_client.get(f"/api/v1/generated-assets/{dto.id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["asset_type"] == "iep"

    def test_get_not_found_returns_404(
        self, authed_client: TestClient, mock_uc: AsyncMock
    ):
        from app.domain.exceptions import AssetNotFoundError

        mock_uc.get_asset.side_effect = AssetNotFoundError("Không tìm thấy")
        # asset_app đã có register_exception_handlers → trả 404 đúng chuẩn
        resp = authed_client.get(f"/api/v1/generated-assets/{uuid.uuid4()}")
        assert resp.status_code == 404
        assert resp.json()["status"] == "error"

    def test_get_without_auth_returns_401(self, anon_client: TestClient):
        resp = anon_client.get(f"/api/v1/generated-assets/{uuid.uuid4()}")
        assert resp.status_code in (401, 402)

    def test_get_invalid_uuid_returns_422(self, authed_client: TestClient):
        resp = authed_client.get("/api/v1/generated-assets/not-a-uuid")
        assert resp.status_code == 422

    def test_get_calls_use_case_with_correct_ids(
        self, authed_client: TestClient, mock_uc: AsyncMock
    ):
        dto = _dto("email")
        mock_uc.get_asset.return_value = dto
        authed_client.get(f"/api/v1/generated-assets/{dto.id}")
        mock_uc.get_asset.assert_called_once_with(
            asset_id=dto.id, requester_id=AI_USER.id
        )
