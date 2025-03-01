from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.sql import delete
from storage.storage_interface import Base, DocumentMetadata, ChunkMetadata
from uuid import UUID

# TODO: the class currently handles basic errors naively, the error handling should be made specific
# and the structure of the class should be made to enable atomicity with concurrent operations
# Inserting/deleting a document's metadata should come with a guaranteed insertion/deletion of all associated chunks
# and vice versa

class MetadataStore:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url)
        self.session_local = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def initialize(self):
        """Create all tables on startup"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
                    
    async def save_document_metadata(self, metadata: DocumentMetadata):
        async with self.session_local() as session:
            try:
                session.add(metadata)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
    
    async def save_chunks(self, chunks: list[ChunkMetadata]):
        async with self.session_local() as session:
            try:
                for chunk in chunks:
                    session.add(chunk)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
    
    async def update_document_status(self, doc_id: UUID, status: str):
        async with self.session_local() as session:
            try:
                doc = await session.get(DocumentMetadata, doc_id)
                if not doc:
                    raise ValueError(f"Document {doc_id} not found.")
                doc.status = status
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
    
    async def delete_document_metadata(self, doc_id: UUID):
        async with self.session_local() as session:
            try:
                doc = await session.get(DocumentMetadata, doc_id)
                if not doc:
                    raise ValueError(f"Document {doc_id} not found.")
                await session.delete(doc)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
    
    async def delete_chunks(self, doc_id: UUID):
        async with self.session_local() as session:
            try:
                result = await session.execute(
                    delete(ChunkMetadata).where(ChunkMetadata.document_id == doc_id)
                )
                await session.commit()
                if result.rowcount == 0:
                    raise ValueError(f"No chunks found for document {doc_id}.")
            except Exception as e:
                await session.rollback()
                raise e
