"""
Outbound Port — Repository Interface cho Class.

Principle (ISP — Interface Segregation):
  Chỉ khai báo những method mà ClassUseCase thực sự gọi qua interface này.
  get_students() bị loại khỏi đây vì UseCase dùng class_.students đã eager-loaded,
  không gọi get_students() qua interface. Nếu cần, gọi trực tiếp trên concrete class.
"""
from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.class_ import Class, ClassStudent


class IClassRepository(ABC):
    """Abstract Port: Contract cho Class data access."""

    @abstractmethod
    async def get_by_id(self, class_id: UUID) -> Class | None: ...

    @abstractmethod
    async def get_by_teacher(self, teacher_id: UUID) -> list[Class]: ...

    @abstractmethod
    async def create(self, teacher_id: UUID, name: str, **kwargs) -> Class: ...

    @abstractmethod
    async def update(self, class_: Class, **kwargs) -> Class: ...

    @abstractmethod
    async def soft_delete(self, class_: Class) -> Class: ...

    @abstractmethod
    async def add_student(self, class_id: UUID, student_id: UUID) -> ClassStudent: ...

    @abstractmethod
    async def remove_student(self, class_id: UUID, student_id: UUID) -> None: ...
    # NOTE: get_students() diện hình không cần trong interface vì ClassUseCase
    # dùng class_.students đã eager-loaded bửi get_by_id().
    # ISP: Interface chỉ có những gì client (UseCase) thực sự cần.

