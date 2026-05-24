"""
Tests cho AI Prompts Router — dùng FastAPI TestClient với mocked Use Case.
Không cần DB thật, override dependency get_use_case và AdminDep.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application.use_cases.ai_prompt_use_case import AIPromptDTO
from app.domain.models.ai_prompt import AIPrompt
from app.entrypoints.api_v1.routers.ai_prompts import get_use_case
from app.core.security import AdminDep

# ── helpers ───────────────────────────────────────────────────────────────────

ADMIN_PAYLOAD = {"sub": "admin-id", "role": "admin", "username": "admin"}


def _dto(
    persona_name: str = "Raina",
    system_prompt_template: str = "You are Raina, a helpful AI assistant.",
    version: str = "v1.0",
) -> AIPromptDTO:
    p = AIPrompt()
    p.id = uuid.uuid4()
    p.persona_name = persona_name
    p.system_prompt_template = system_prompt_template
    p.version = version
    p.updated_at = datetime.now(timezone.utc)
    return AIPromptDTO.from_orm(p)


@pytest.fixture
def mock_uc() -> AsyncMock:
    """AsyncMock không spec để tất cả methods đều là awaitable."""
    return AsyncMock()


@pytest.fixture
def authed_client(test_app: FastAPI, mock_uc: AsyncMock) -> TestClient:
    """Client đã override AdminDep (admin) + use_case."""
    test_app.dependency_overrides[AdminDep] = lambda: ADMIN_PAYLOAD
    test_app.dependency_overrides[get_use_case] = lambda: mock_uc
    with TestClient(test_app, raise_server_exceptions=True) as c:
        yield c
    test_app.dependency_overrides.clear()


@pytest.fixture
def anon_client(test_app: FastAPI) -> TestClient:
    """Client không có auth — dùng để test 401/403."""
    test_app.dependency_overrides.clear()
    with TestClient(test_app, raise_server_exceptions=False) as c:
        yield c


# ── POST /ai-prompts ──────────────────────────────────────────────────────────


class TestPostAIPrompt:
    def test_create_returns_201(self, authed_client, mock_uc):
        dto = _dto("Raina")
        mock_uc.create.return_value = dto

        resp = authed_client.post(
            "/api/v1/ai-prompts",
            json={
                "persona_name": "Raina",
                "system_prompt_template": "You are Raina, a helpful AI assistant.",
                "version": "v1.0",
            },
        )

        assert resp.status_code == 201
        assert resp.json()["status"] == "success"
        assert resp.json()["data"]["persona_name"] == "Raina"
        mock_uc.create.assert_called_once()

    def test_create_without_auth_returns_403_or_401(self, anon_client):
        resp = anon_client.post(
            "/api/v1/ai-prompts",
            json={
                "persona_name": "Raina",
                "system_prompt_template": "You are Raina, a helpful AI assistant.",
            },
        )
        assert resp.status_code in (401, 403)

    def test_create_missing_required_field_returns_422(self, authed_client):
        resp = authed_client.post(
            "/api/v1/ai-prompts",
            json={"persona_name": "Raina"},  # thiếu system_prompt_template
        )
        assert resp.status_code == 422


# ── GET /ai-prompts ───────────────────────────────────────────────────────────


class TestGetListAIPrompts:
    def test_list_returns_200_with_data(self, authed_client, mock_uc):
        mock_uc.list_all.return_value = [_dto("Raina"), _dto("Tutor"), _dto("StudyBot")]

        resp = authed_client.get("/api/v1/ai-prompts")

        assert resp.status_code == 200
        assert resp.json()["status"] == "success"
        assert len(resp.json()["data"]) == 3

    def test_list_empty_returns_200(self, authed_client, mock_uc):
        mock_uc.list_all.return_value = []

        resp = authed_client.get("/api/v1/ai-prompts")

        assert resp.status_code == 200
        assert resp.json()["data"] == []


# ── GET /ai-prompts/{id} ──────────────────────────────────────────────────────


class TestGetAIPromptById:
    def test_get_by_id_returns_200(self, authed_client, mock_uc):
        dto = _dto("Raina")
        mock_uc.get_by_id.return_value = dto

        resp = authed_client.get(f"/api/v1/ai-prompts/{dto.id}")

        assert resp.status_code == 200
        assert resp.json()["data"]["persona_name"] == "Raina"

    def test_get_by_id_no_auth_still_works(self, test_app, mock_uc):
        """GET /{id} không cần auth."""
        test_app.dependency_overrides[get_use_case] = lambda: mock_uc
        dto = _dto()
        mock_uc.get_by_id.return_value = dto

        with TestClient(test_app) as c:
            resp = c.get(f"/api/v1/ai-prompts/{dto.id}")

        test_app.dependency_overrides.clear()
        assert resp.status_code == 200


# ── PATCH /ai-prompts/{id} ────────────────────────────────────────────────────


class TestPatchAIPrompt:
    def test_patch_version_returns_200(self, authed_client, mock_uc):
        updated = _dto(version="v2.0")
        mock_uc.update.return_value = updated

        resp = authed_client.patch(
            f"/api/v1/ai-prompts/{updated.id}",
            json={"version": "v2.0"},
        )

        assert resp.status_code == 200
        assert resp.json()["data"]["version"] == "v2.0"

    def test_patch_template_returns_200(self, authed_client, mock_uc):
        new_template = "Updated prompt for Raina — now more engaging and fun!"
        updated = _dto(system_prompt_template=new_template)
        mock_uc.update.return_value = updated

        resp = authed_client.patch(
            f"/api/v1/ai-prompts/{updated.id}",
            json={"system_prompt_template": new_template},
        )

        assert resp.status_code == 200
        assert resp.json()["data"]["system_prompt_template"] == new_template

    def test_patch_without_auth_returns_401_or_403(self, anon_client):
        resp = anon_client.patch(
            f"/api/v1/ai-prompts/{uuid.uuid4()}",
            json={"version": "v2.0"},
        )
        assert resp.status_code in (401, 403)
