"""
Tests cho AIPromptUseCase — unit tests với mock repository.
Không cần DB thật, dùng unittest.mock.AsyncMock.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.application.use_cases.ai_prompt_use_case import AIPromptDTO, AIPromptUseCase
from app.domain.models.ai import AIPrompt

# ── helpers ──────────────────────────────────────────────────────────────────


def _make_prompt(
    persona_name: str = "Raina",
    system_prompt_template: str = "You are Raina, a helpful AI assistant for Q-School.",
    version: str = "v1.0",
) -> AIPrompt:
    """Tạo AIPrompt ORM object giả để dùng trong tests."""
    p = AIPrompt()
    p.id = uuid.uuid4()
    p.persona_name = persona_name
    p.system_prompt_template = system_prompt_template
    p.version = version
    p.updated_at = datetime.now(timezone.utc)
    return p


def run(coro):
    """Chạy coroutine đồng bộ trong tests."""
    return asyncio.run(coro)


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def use_case(mock_repo: AsyncMock) -> AIPromptUseCase:
    return AIPromptUseCase(mock_repo)


# ── CREATE ────────────────────────────────────────────────────────────────────


class TestCreate:
    def test_create_success_returns_dto(self, use_case, mock_repo):
        prompt = _make_prompt()
        mock_repo.get_by_persona_name.return_value = None
        mock_repo.create.return_value = prompt

        result = run(use_case.create("Raina", prompt.system_prompt_template, "v1.0"))

        assert isinstance(result, AIPromptDTO)
        assert result.persona_name == "Raina"
        assert result.version == "v1.0"
        mock_repo.create.assert_called_once_with(
            "Raina", prompt.system_prompt_template, "v1.0"
        )

    def test_create_duplicate_persona_raises_409(self, use_case, mock_repo):
        mock_repo.get_by_persona_name.return_value = _make_prompt()

        with pytest.raises(HTTPException) as exc:
            run(use_case.create("Raina", "Some prompt text here.", "v1.0"))

        assert exc.value.status_code == 409
        mock_repo.create.assert_not_called()


# ── GET BY ID ─────────────────────────────────────────────────────────────────


class TestGetById:
    def test_get_by_id_found(self, use_case, mock_repo):
        prompt = _make_prompt("Tutor")
        mock_repo.get_by_id.return_value = prompt

        result = run(use_case.get_by_id(prompt.id))

        assert result.id == prompt.id
        assert result.persona_name == "Tutor"

    def test_get_by_id_not_found_raises_404(self, use_case, mock_repo):
        mock_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            run(use_case.get_by_id(uuid.uuid4()))

        assert exc.value.status_code == 404


# ── GET BY PERSONA NAME ───────────────────────────────────────────────────────


class TestGetByPersonaName:
    def test_found(self, use_case, mock_repo):
        mock_repo.get_by_persona_name.return_value = _make_prompt("StudyBot")

        result = run(use_case.get_by_persona_name("StudyBot"))

        assert result.persona_name == "StudyBot"

    def test_not_found_raises_404(self, use_case, mock_repo):
        mock_repo.get_by_persona_name.return_value = None

        with pytest.raises(HTTPException) as exc:
            run(use_case.get_by_persona_name("Unknown"))

        assert exc.value.status_code == 404


# ── LIST ALL ──────────────────────────────────────────────────────────────────


class TestListAll:
    def test_returns_list_of_dtos(self, use_case, mock_repo):
        mock_repo.list_all.return_value = [
            _make_prompt("Raina"),
            _make_prompt("Tutor"),
            _make_prompt("StudyBot"),
        ]

        result = run(use_case.list_all())

        assert len(result) == 3
        assert all(isinstance(r, AIPromptDTO) for r in result)

    def test_returns_empty_list(self, use_case, mock_repo):
        mock_repo.list_all.return_value = []

        result = run(use_case.list_all())

        assert result == []


# ── UPDATE ────────────────────────────────────────────────────────────────────


class TestUpdate:
    def test_update_version_success(self, use_case, mock_repo):
        prompt_id = uuid.uuid4()
        original = _make_prompt()
        original.id = prompt_id
        updated = _make_prompt(version="v2.0")
        updated.id = prompt_id

        mock_repo.get_by_id.return_value = original
        mock_repo.update.return_value = updated

        result = run(use_case.update(prompt_id, None, "v2.0"))

        assert result.version == "v2.0"
        mock_repo.update.assert_called_once_with(prompt_id, None, "v2.0")

    def test_update_template_success(self, use_case, mock_repo):
        prompt_id = uuid.uuid4()
        original = _make_prompt()
        original.id = prompt_id
        new_template = "New improved system prompt for Raina persona."
        updated = _make_prompt(system_prompt_template=new_template)
        updated.id = prompt_id

        mock_repo.get_by_id.return_value = original
        mock_repo.update.return_value = updated

        result = run(use_case.update(prompt_id, new_template, None))

        assert result.system_prompt_template == new_template

    def test_update_not_found_raises_404(self, use_case, mock_repo):
        mock_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc:
            run(use_case.update(uuid.uuid4(), "new prompt text here", None))

        assert exc.value.status_code == 404

    def test_update_repo_returns_none_raises_404(self, use_case, mock_repo):
        prompt_id = uuid.uuid4()
        original = _make_prompt()
        original.id = prompt_id

        # get_by_id trả về prompt (pass lần 1), update trả None (lỗi)
        mock_repo.get_by_id.return_value = original
        mock_repo.update.return_value = None

        with pytest.raises(HTTPException) as exc:
            run(use_case.update(prompt_id, "Updated content here.", None))

        assert exc.value.status_code == 404


# ── DTO ───────────────────────────────────────────────────────────────────────


class TestAIPromptDTO:
    def test_from_orm(self):
        prompt = _make_prompt("Raina", "You are Raina.", "v1.5")

        dto = AIPromptDTO.from_orm(prompt)

        assert dto.id == prompt.id
        assert dto.persona_name == "Raina"
        assert dto.system_prompt_template == "You are Raina."
        assert dto.version == "v1.5"
        assert dto.updated_at == prompt.updated_at
