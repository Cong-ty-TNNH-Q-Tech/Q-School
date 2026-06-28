from typing import Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_type: str
    s3_url: str
    is_public: bool
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
