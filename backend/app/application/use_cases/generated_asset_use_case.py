"""
Use Case: GeneratedAssetUseCase
Business logic: gọi LLM để sinh nội dung giáo dục, lưu kết quả.
Không biết gì về HTTP hay Database — phụ thuộc hoàn toàn vào Port.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.application.ports.outbound.generated_asset_repository import (
    GeneratedAssetRepository,
)
from app.core.exceptions import NotFoundException, ValidationException
from app.domain.models.ai import GeneratedAsset

VALID_ASSET_TYPES = frozenset(
    {
        "lesson_plan",
        "quiz",
        "email",
        "iep",
        "behavior_intervention",
        "report_comment",
    }
)


# ── DTO ───────────────────────────────────────────────────────────────────────


@dataclass
class GeneratedAssetDTO:
    """Data Transfer Object — tách biệt domain model với HTTP layer."""

    id: uuid.UUID
    creator_id: uuid.UUID
    asset_type: str
    input_params: dict[str, Any]
    output_content: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj: GeneratedAsset) -> "GeneratedAssetDTO":
        return cls(
            id=obj.id,
            creator_id=obj.creator_id,
            asset_type=obj.asset_type,
            input_params=obj.input_params or {},
            output_content=obj.output_content or {},
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


@dataclass
class PaginatedAssetsDTO:
    """Wrapper cho cursor-paginated list."""

    items: list[GeneratedAssetDTO] = field(default_factory=list)
    next_cursor_created_at: str | None = None
    next_cursor_id: str | None = None
    has_more: bool = False


# ── Use Case ──────────────────────────────────────────────────────────────────


class GeneratedAssetUseCase:
    """
    Single-Responsibility: chỉ xử lý logic nghiệp vụ Generated Assets.
    LLM client được inject qua constructor (Dependency Inversion).
    """

    _LIMIT_MAX = 50
    _LIMIT_DEFAULT = 20

    def __init__(
        self,
        repo: GeneratedAssetRepository,
        llm_client: Any | None = None,
    ) -> None:
        self._repo = repo
        self._llm = llm_client  # None trong unit tests

    # ── Private helpers ──────────────────────────────────────────────────────

    def _validate_asset_type(self, asset_type: str) -> None:
        if asset_type not in VALID_ASSET_TYPES:
            raise ValidationException(
                f"asset_type '{asset_type}' không hợp lệ. "
                f"Các giá trị cho phép: {sorted(VALID_ASSET_TYPES)}"
            )

    async def _call_llm(
        self, asset_type: str, input_params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Gọi LLM (vLLM / OpenAI-compatible) để sinh nội dung.
        - Nếu llm_client là None (unit test) → trả về mock output.
        - Nếu LLM lỗi → raise Exception (bắt ở router layer).
        """
        if self._llm is None:
            # Fallback cho test / dev khi chưa có vLLM
            return {
                "content": f"[Mock AI output for {asset_type}]",
                "tokens_used": 0,
            }

        # Build prompt dựa trên asset_type
        prompt = self._build_prompt(asset_type, input_params)

        response = await self._llm.chat.completions.create(
            model="default",
            messages=[
                {
                    "role": "system",
                    "content": self._system_prompt(asset_type),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2048,
        )

        text = response.choices[0].message.content or ""
        return {
            "content": text,
            "tokens_used": response.usage.total_tokens if response.usage else 0,
        }

    def _system_prompt(self, asset_type: str) -> str:
        prompts = {
            "email": (
                "Bạn là giáo viên chuyên nghiệp. "
                "Hãy soạn email cho phụ huynh bằng tiếng Việt, "
                "lịch sự, rõ ràng và đầy đủ thông tin."
            ),
            "iep": (
                "Bạn là chuyên gia giáo dục đặc biệt. "
                "Hãy soạn Kế hoạch Giáo dục Cá nhân (IEP) chi tiết, "
                "theo chuẩn quốc tế, bằng tiếng Việt."
            ),
            "behavior_intervention": (
                "Bạn là chuyên gia tâm lý học đường. "
                "Hãy soạn kế hoạch can thiệp hành vi học sinh "
                "theo phương pháp PBIS bằng tiếng Việt."
            ),
            "report_comment": (
                "Bạn là giáo viên chủ nhiệm. "
                "Hãy soạn nhận xét học bạ học sinh, "
                "tích cực, cụ thể và có tính khích lệ, bằng tiếng Việt."
            ),
            "lesson_plan": (
                "Bạn là giáo viên giàu kinh nghiệm. "
                "Hãy soạn giáo án chi tiết theo chuẩn Bộ GD&ĐT Việt Nam."
            ),
            "quiz": (
                "Bạn là giáo viên. "
                "Hãy tạo bộ câu hỏi kiểm tra phù hợp, "
                "đa dạng về mức độ nhận thức (Bloom's Taxonomy), bằng tiếng Việt."
            ),
        }
        return prompts.get(asset_type, "Bạn là trợ lý AI giáo dục chuyên nghiệp.")

    def _build_prompt(self, asset_type: str, params: dict[str, Any]) -> str:
        """Chuyển input_params thành prompt text."""
        lines = [f"Loại nội dung: {asset_type.upper()}", "Thông tin đầu vào:"]
        for key, value in params.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    # ── Public methods ────────────────────────────────────────────────────────

    async def generate_asset(
        self,
        creator_id: uuid.UUID,
        asset_type: str,
        input_params: dict[str, Any],
    ) -> GeneratedAssetDTO:
        """
        Sinh nội dung AI và lưu vào DB.
        1. Validate asset_type
        2. Gọi LLM
        3. Lưu kết quả vào DB
        """
        self._validate_asset_type(asset_type)
        output_content = await self._call_llm(asset_type, input_params)
        asset = await self._repo.create(
            creator_id=creator_id,
            asset_type=asset_type,
            input_params=input_params,
            output_content=output_content,
        )
        return GeneratedAssetDTO.from_orm(asset)

    async def get_asset(
        self, asset_id: uuid.UUID, requester_id: uuid.UUID
    ) -> GeneratedAssetDTO:
        """Lấy asset theo ID. Chỉ creator mới được xem."""
        asset = await self._repo.get_by_id(asset_id)
        if not asset:
            raise NotFoundException(f"Không tìm thấy asset với id={asset_id}.")
        if asset.creator_id != requester_id:
            raise NotFoundException(
                f"Không tìm thấy asset với id={asset_id}."
            )  # Ẩn 403 → trả 404 để không lộ existence
        return GeneratedAssetDTO.from_orm(asset)

    async def list_assets(
        self,
        creator_id: uuid.UUID,
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = _LIMIT_DEFAULT,
    ) -> PaginatedAssetsDTO:
        """Cursor-paginated list assets của user."""
        limit = min(limit, self._LIMIT_MAX)
        # Lấy thêm 1 record để biết có trang tiếp theo không
        rows = await self._repo.list_by_creator(
            creator_id=creator_id,
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
            limit=limit + 1,
        )

        has_more = len(rows) > limit
        items = rows[:limit]

        next_cursor_created_at: str | None = None
        next_cursor_id: str | None = None
        if has_more and items:
            last = items[-1]
            next_cursor_created_at = last.created_at.isoformat()
            next_cursor_id = str(last.id)

        return PaginatedAssetsDTO(
            items=[GeneratedAssetDTO.from_orm(r) for r in items],
            next_cursor_created_at=next_cursor_created_at,
            next_cursor_id=next_cursor_id,
            has_more=has_more,
        )
