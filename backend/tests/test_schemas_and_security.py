"""
Tests cho Pydantic Schemas và Security module.
"""

import uuid

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.entrypoints.api_v1.schemas.ai_prompt_schemas import (
    AIPromptListResponse,
    AIPromptResponse,
    AIPromptSingleResponse,
    CreateAIPromptRequest,
    UpdateAIPromptRequest,
)

# ── CreateAIPromptRequest ─────────────────────────────────────────────────────


class TestCreateAIPromptRequest:
    def test_valid_minimal(self):
        req = CreateAIPromptRequest(
            persona_name="Raina",
            system_prompt_template="You are Raina, a helpful AI assistant.",
        )
        assert req.persona_name == "Raina"
        assert req.version == "v1.0"  # default

    def test_valid_with_version(self):
        req = CreateAIPromptRequest(
            persona_name="Tutor",
            system_prompt_template="You are Tutor, patient and clear.",
            version="v2.0",
        )
        assert req.version == "v2.0"

    def test_empty_persona_name_raises(self):
        with pytest.raises(ValidationError):
            CreateAIPromptRequest(
                persona_name="",
                system_prompt_template="You are Raina, a helpful AI assistant.",
            )

    def test_template_too_short_raises(self):
        with pytest.raises(ValidationError):
            CreateAIPromptRequest(
                persona_name="Raina",
                system_prompt_template="Short",  # < 10 chars
            )

    def test_persona_name_too_long_raises(self):
        with pytest.raises(ValidationError):
            CreateAIPromptRequest(
                persona_name="A" * 101,  # > 100 chars
                system_prompt_template="You are a helpful AI assistant.",
            )


# ── UpdateAIPromptRequest ─────────────────────────────────────────────────────


class TestUpdateAIPromptRequest:
    def test_all_optional_empty(self):
        req = UpdateAIPromptRequest()
        assert req.system_prompt_template is None
        assert req.version is None

    def test_version_only(self):
        req = UpdateAIPromptRequest(version="v3.0")
        assert req.version == "v3.0"
        assert req.system_prompt_template is None

    def test_template_only(self):
        req = UpdateAIPromptRequest(
            system_prompt_template="Updated system prompt content here."
        )
        assert req.system_prompt_template is not None
        assert req.version is None

    def test_version_too_long_raises(self):
        with pytest.raises(ValidationError):
            UpdateAIPromptRequest(version="v" * 21)  # > 20 chars


# ── Response Schemas ──────────────────────────────────────────────────────────


class TestResponseSchemas:
    def _sample_response(self) -> AIPromptResponse:
        from datetime import datetime, timezone

        return AIPromptResponse(
            id=uuid.uuid4(),
            persona_name="Raina",
            system_prompt_template="You are Raina.",
            version="v1.0",
            updated_at=datetime.now(timezone.utc),
        )

    def test_single_response_status_success(self):
        data = self._sample_response()
        resp = AIPromptSingleResponse(data=data)
        assert resp.status == "success"
        assert resp.data.persona_name == "Raina"

    def test_list_response_status_success(self):
        data = [self._sample_response(), self._sample_response()]
        resp = AIPromptListResponse(data=data)
        assert resp.status == "success"
        assert len(resp.data) == 2

    def test_list_response_empty(self):
        resp = AIPromptListResponse(data=[])
        assert resp.data == []


# ── Security module ───────────────────────────────────────────────────────────


class TestSecurity:
    def _make_token(self, payload: dict) -> str:
        from jose import jwt

        from app.core.config import settings

        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def test_decode_valid_access_token(self):
        from datetime import datetime, timedelta, timezone

        from app.core.security import decode_token

        token = self._make_token(
            {
                "sub": "user-1",
                "role": "admin",
                "type": "access",
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
                "iat": datetime.now(timezone.utc),
            }
        )
        payload = decode_token(token)
        assert payload["role"] == "admin"
        assert payload["sub"] == "user-1"

    def test_decode_invalid_token_raises_jwt_error(self):
        from jose import JWTError

        from app.core.security import decode_token

        with pytest.raises(JWTError):
            decode_token("invalid.token.here")

    def test_decode_expired_token_raises_jwt_error(self):
        from datetime import datetime, timedelta, timezone

        from jose import JWTError

        from app.core.security import decode_token

        token = self._make_token(
            {
                "sub": "user-1",
                "type": "access",
                "exp": datetime.now(timezone.utc) - timedelta(hours=1),  # expired
                "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            }
        )
        with pytest.raises(JWTError):
            decode_token(token)
