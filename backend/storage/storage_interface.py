from sqlalchemy.dialects.postgresql import UUID as sqlUUID
from uuid import UUID;
from typing import Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey
from datetime import datetime
from pydantic import BaseModel

class Base(DeclarativeBase):
    pass

class DocumentMetadataBase(BaseModel):
    id: UUID
    filename: str
    mime_type: str
    size_bytes: int
    status: str = "pending"
    created_at: datetime = datetime.now()

class DocumentMetadata(Base):
    __tablename__ = "documents"
    
    id: Mapped[UUID] = mapped_column(sqlUUID, primary_key=True)
    filename: Mapped[str] = mapped_column(String)
    mime_type: Mapped[str] = mapped_column(String)
    size_bytes: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    def model_dump_json(self) -> str:
        return DocumentMetadataBase(
            id=self.id,
            filename=self.filename,
            mime_type=self.mime_type,
            size_bytes=self.size_bytes,
            status=self.status or "pending",
            created_at=self.created_at or datetime.now()
        ).model_dump_json()
    def __eq__(self, other):
        if not isinstance(other, DocumentMetadata):
            return False
        return (
            self.id == other.id and
            self.filename == other.filename and
            self.mime_type == other.mime_type and
            self.size_bytes == other.size_bytes
        )

class ChunkMetadata(Base):
    __tablename__ = "chunks"
    
    id: Mapped[UUID] = mapped_column(sqlUUID, primary_key=True)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id"))
    content: Mapped[str] = mapped_column(String)
    sequence: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    embedding_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    def __eq__(self, other):
        if not isinstance(other, ChunkMetadata):
            return False
        return (
                self.id == other.id and
                self.document_id == other.document_id and
                self.content == other.content and
                self.sequence == other.sequence and
                self.embedding_id == other.embedding_id
            )
    

class StorageInterface:
    """Abstract base class for all storage operations"""
    
    async def save_document(self, content: bytes, metadata: DocumentMetadata) -> UUID:
        """Save document and return its ID"""
        raise NotImplementedError
        
    async def save_chunks(self, doc_id: UUID, chunks: list[ChunkMetadata]) -> bool:
        """Save document chunks"""
        raise NotImplementedError
        
    async def get_document(self, doc_id: UUID) -> Optional[bytes]:
        """Retrieve document content"""
        raise NotImplementedError
        
    async def get_chunks(self, doc_id: UUID) -> list[ChunkMetadata]:
        """Retrieve all chunks for a document"""
        raise NotImplementedError
        
    async def delete_document(self, doc_id: UUID) -> bool:
        """Delete document and all associated data"""
        raise NotImplementedError
