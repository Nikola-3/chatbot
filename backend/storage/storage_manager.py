from uuid import uuid4, UUID
import magic
from .file_system_storage import FileSystemStorage
from .vector_storage import VectorStorage
from .metadata_store import MetadataStore
from .storage_interface import DocumentMetadata, ChunkMetadata
from processing.doc_status import DocumentStatus
from datetime import datetime, timezone

# TODO: Currently, operations can fail intermittently and leave the storage in an inconsistent state
# implement proper error handling to make the operations atomic, perhaps using sqlalchely's begin
# clause and passing the session to the method

class StorageManager:
    """Coordinates between different storage systems"""
    
    def __init__(
        self,
        file_storage: FileSystemStorage,
        vector_storage: VectorStorage,
        metadata_storage: MetadataStore
    ):
        self.files = file_storage
        self.vectors = vector_storage
        self.metadata = metadata_storage
        self.mime = magic.Magic(mime=True)
    
    async def save_document(self, content: bytes, filename: str) -> UUID:
        """Complete save operation of unprocessed file"""
        doc_id = uuid4()
        mime_type = self.mime.from_buffer(content)
        metadata = DocumentMetadata(
            id=doc_id,
            filename=filename,
            mime_type=mime_type,
            size_bytes=len(content),
            status="pending",
            created_at=datetime.now()
        )
        try:
            await self.files.save_document(content, metadata)
            await self.metadata.save_document_metadata(metadata)
        except Exception as e:
            raise e
        
        return doc_id

    async def save_processed_chunks(
        self,
        doc_id: UUID,
        chunks: list[ChunkMetadata],
        embeddings: list[list[float]]
    ):
        """Save processed chunks and their embeddings"""
        await self.metadata.update_document_status(doc_id, DocumentStatus.STORING.value)
        try:
            await self.metadata.save_chunks(chunks)
            await self.vectors.add_chunks(chunks, embeddings)
            await self.metadata.update_document_status(doc_id, "processed")
        except Exception as e:
            raise e                         
    
    async def delete_document(self, doc_id: UUID) -> bool:
        """Delete document and all associated data"""
        try:
            file_deleted = await self.files.delete_document(doc_id)
            
            await self.metadata.delete_document_metadata(doc_id)
            await self.metadata.delete_chunks(doc_id)
            
            await self.vectors.delete_chunks(doc_id)
            
            return file_deleted
        except Exception as e:
                # TODO: Proper error handling
                raise e
