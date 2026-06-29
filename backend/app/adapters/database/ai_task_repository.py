from uuid import UUID
from typing import Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database.base import BaseRepository
from app.application.ports.outbound.ai_repository import IAITaskRepository
from app.domain.models.ai import AITask


class SQLAlchemyAITaskRepository(BaseRepository[AITask], IAITaskRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(AITask, session)

    async def create(self, user_id: UUID, task_type: str) -> AITask:
        task = AITask(user_id=user_id, task_type=task_type, status="pending")
        self.db.add(task)
        await self.db.flush()
        return task

    async def update_status(
        self,
        task: AITask,
        status: str,
        result_payload: dict[str, Any] | None = None,
    ) -> AITask:
        from sqlalchemy import func
        task.status = status
        if result_payload is not None:
            task.result_payload = result_payload
        if status in ("completed", "failed"):
            task.completed_at = func.now()
        await self.db.flush()
        return task

    async def get_by_id(self, task_id: UUID) -> AITask | None:
        stmt = select(AITask).where(AITask.id == task_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
