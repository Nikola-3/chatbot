from uuid import UUID, uuid4
from openai import AsyncOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from unstructured.partition.auto import partition
from io import BytesIO

from processing.config import ProcessingConfig
from processing.doc_status import DocumentStatus
from processing.exceptions import ProcessingError, ExtractionError, EmbeddingError
from storage.storage_manager import StorageManager
from storage.storage_interface import ChunkMetadata

# this constant decides how many whitespace characters we control for in small file entries
# too big and we will be running strip on unnecessarily large files
# too small and a few whitespaces will result in the file being ignored for context
WHITESPACE_COEFF = 2

class DocumentProcessor:
    def __init__(
        self,
        storage: StorageManager,
        openai_client: AsyncOpenAI,
        config: ProcessingConfig
    ):
        self.storage = storage
        self.openai = openai_client
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    async def process_document(self, content: bytes, filename: str) -> UUID:
        """Process a document through the entire pipeline"""
        doc_id = None
        try:
            doc_id = await self.storage.save_document(content, filename)

            text = await self._extract_text(content, doc_id)
            
            chunks = await self._create_chunks(text, doc_id)
            if not chunks:
                raise ProcessingError("No valid chunks created")
            
            chunk_metadatas = [ChunkMetadata(id=uuid4(), document_id=doc_id, content=chunks[i], sequence=i) for i in range(len(chunks))]

            # TODO: embeddings = await self._generate_embeddings(chunks, doc_id)
            await self.storage.save_processed_chunks(doc_id, chunk_metadatas, [[0.0]]) # TODO: embeddings
            
            await self.storage.metadata.update_document_status(doc_id, DocumentStatus.COMPLETED.value)
            return doc_id

        except Exception as e:
            await self.storage.metadata.update_document_status(doc_id or "", DocumentStatus.FAILED.value)
            if doc_id:
                await self._cleanup_on_error(doc_id)
            raise ProcessingError(f"Document processing failed: {str(e)}") from e

    async def _extract_text(self, contents: bytes, doc_id: UUID) -> str:
        """Extract text from document content"""
        await self.storage.metadata.update_document_status(doc_id, DocumentStatus.EXTRACTING.value)
        try:
            elements = partition(file=BytesIO(contents))
            return "\n\n".join([str(el) for el in elements])
        except Exception as e:
            raise ExtractionError(f"Text extraction failed: {str(e)}") from e


    async def _create_chunks(self, text: str, doc_id: UUID) -> list[ChunkMetadata]:
        """Split text into chunks"""
        await self.storage.metadata.update_document_status(doc_id, DocumentStatus.CHUNKING.value)
        
        if len(text) <= WHITESPACE_COEFF * self.config.min_chunk_size and len(text.strip()) <= self.config.min_chunk_size:
            # If entire text is shorter than min_chunk_size, return it as a single chunk
            return [text.strip()]
        chunks = self.text_splitter.split_text(text)
        return [chunk for chunk in chunks 
                if len(chunk.strip()) >= self.config.min_chunk_size]
    
    async def _generate_embeddings(self, texts: list[str], doc_id: UUID) -> list[list[float]]:
        """Generate embeddings for chunks"""
        await self.storage.metadata.update_document_status(doc_id, DocumentStatus.EMBEDDING.value)
        try:
            response = await self.openai.embeddings.create(
                model=self.config.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise EmbeddingError(f"Embedding generation failed: {str(e)}") from e

    async def _cleanup_on_error(self, doc_id: UUID) -> None:
        """Clean up any stored data if processing fails"""
        try:
            await self.storage.delete_document(doc_id)
            await self.storage.delete_chunks(doc_id)
        except Exception:
            pass
