from openai import AsyncOpenAI

from processing.config import ProcessingConfig
from processing.exceptions import ProcessingError, EmbeddingError
from storage.storage_manager import StorageManager
from storage.storage_interface import ChunkMetadata
from uuid import UUID

class ChunkResult(dict):
    content: str
    document_id: str
    sequence: int
    embedding_id: str

class QueryResult(dict):
    query: str
    chunks: list[ChunkResult]
    context: str

class QueryProcessor:
    def __init__(
        self,
        storage: StorageManager,
        openai_client: AsyncOpenAI,
        config: ProcessingConfig
    ):
        self.storage = storage
        self.openai = openai_client
        self.config = config

    async def process_query(self, query: str, limit: int = 3) -> QueryResult:
        """Process a query and retrieve relevant context"""
        try:
            # TODO: Fix query embedding generation
            # Generate query embedding
            query_embedding = None # await self._generate_embedding(query)
            

            # Retrieve relevant chunks
            # chunks = await get_relevant_chunks(
            #     embedding=query_embedding,
            #     limit=limit
            # )

            
            # if not chunks:
            #     return {
            #         "query": query,
            #         "chunks": [],
            #         "context": "",
            #     }

            # Format context from chunks
            # context = self._format_context(chunks)
            
            return {
                "query": query,
                "chunks": None, #chunks,
                "context": "", #context,
            }

        except Exception as e:
            raise ProcessingError(f"Query processing failed: {str(e)}") from e

    async def _generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text"""
        try:
            response = await self.openai.embeddings.create(
                model=self.config.embedding_model,
                input=[text]
            )
            return response.data[0].embedding
        except Exception as e:
            raise EmbeddingError(f"Failed to generate query embedding: {str(e)}") from e

    def _format_context(self, chunks: list[ChunkResult]) -> str:
        """Format retrieved chunks into a single context string"""
        formatted_chunks = []
        for i, chunk in enumerate(chunks, 1):
            formatted_chunks.append(f"[{i}] {chunk['content']}")
        return "\n\n".join(formatted_chunks)

    async def get_relevant_chunks(self, query_embedding: list[float], limit: int = 5) -> list[ChunkMetadata]:
        """Get chunks relevant to the query using vector similarity search"""
        try:
            search_results = await self.storage.vectors.search(query_embedding, limit=limit)
            
            # Process the search results into ChunkMetadata objects
            chunks = []
            for i in range(len(search_results['ids'][0])):
                chunk = ChunkMetadata(
                    id=UUID(search_results['ids'][0][i]),
                    document_id=UUID(search_results['metadatas'][0][i]['document_id']),
                    sequence=search_results['metadatas'][0][i]['sequence'],
                    content=search_results['documents'][0][i],
                    embedding_id=search_results['ids'][0][i]
                )
                chunks.append(chunk)
            
            return chunks

        except Exception as e:
            raise ProcessingError(f"Error retrieving relevant chunks: {str(e)}")