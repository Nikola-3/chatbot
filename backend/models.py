from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class ChatMessage(BaseModel):
    content: str

class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []

class Document(BaseModel):
    id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    upload_date: datetime
    status: str

class ProcessingStatus(BaseModel):
    status: str
    message: Optional[str] = None
