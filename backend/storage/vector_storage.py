from chromadb import Client
from chromadb.config import Settings
from .storage_interface import ChunkMetadata
from uuid import UUID

class VectorStorage:
    def __init__(self, persist_dir: str):
        self.client = Client(Settings(
            persist_directory=persist_dir,
            is_persistent=True
        ))
        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )
    
    async def add_chunks(self, chunks: list[ChunkMetadata], embeddings: list[list[float]]):
        """Add chunks with their embeddings to vector store"""
        for chunk in chunks:
            ids = [str(chunk.id)]
            metadatas=[{
                "document_id": str(chunk.document_id),
                "sequence": chunk.sequence
            }]
            documents=[chunk.content]
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
    
    async def search(self, query_embedding: list[float], limit: int = 5) -> list[dict]:
        """Search for similar chunks"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=["metadatas", "documents", "distances"]
        )
        
        return results
    
    async def delete_chunks(self, doc_id: UUID):
        """Delete chunks associated with a document ID"""
        chunk_ids = [str(chunk.id) for chunk in await self.get_chunks_by_document_id(doc_id)]
        if chunk_ids:
            await self.collection.delete(ids=chunk_ids)
    
    async def get_chunks_by_document_id(self, doc_id: UUID) -> list[ChunkMetadata]:
        """Retrieve chunks by document ID"""
        results = await self.collection.query(
            query_filter={"document_id": str(doc_id)},
            include=["metadatas", "documents"]
        )
        return [
            ChunkMetadata(
                id=UUID(result["id"]),
                document_id=UUID(result["metadata"]["document_id"]),
                sequence=result["metadata"]["sequence"],
                content=result["document"],
                embedding_id=result["id"]
            )
            for result in results
        ]
