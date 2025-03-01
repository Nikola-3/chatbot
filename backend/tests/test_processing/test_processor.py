import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import UUID

from processing.processor import DocumentProcessor
from processing.config import ProcessingConfig
from processing.exceptions import ProcessingError
from processing.doc_status import DocumentStatus
from storage.storage_manager import StorageManager

@pytest.fixture
def mock_storage():
    storage = Mock(spec=StorageManager)
    storage.save_document = AsyncMock(return_value=UUID('12345678-1234-5678-1234-567812345678'))
    storage.save_processed_chunks = AsyncMock()
    storage.delete_document = AsyncMock()
    storage.delete_chunks = AsyncMock()
    storage.metadata = Mock()
    storage.metadata.update_document_status = AsyncMock()
    return storage

@pytest.fixture
def mock_openai():
    client = AsyncMock()
    client.embeddings.create = AsyncMock(return_value=Mock(
        data=[Mock(embedding=[0.1, 0.2, 0.3])]
    ))
    return client

@pytest.fixture
def config():
    return ProcessingConfig(
        chunk_size=100,
        chunk_overlap=20,
        min_chunk_size=50
    )

@pytest.fixture
def processor(mock_storage, mock_openai, config):
    return DocumentProcessor(
        storage=mock_storage,
        openai_client=mock_openai,
        config=config
    )

@pytest.mark.asyncio
async def test_process_document_success(processor, mock_storage):
    # Given
    file_content = b"Test document content"
    filename = "test.txt"
    
    # When
    doc_id = await processor.process_document(file_content, filename)
    
    # Then
    assert isinstance(doc_id, UUID)
    mock_storage.save_document.assert_called_once_with(file_content, filename)
    mock_storage.save_processed_chunks.assert_called_once()
    mock_storage.metadata.update_document_status.assert_called_with(
        doc_id,
        DocumentStatus.COMPLETED.value
    )

@pytest.mark.asyncio
async def test_extraction_error_handling(processor, mock_storage):
    # Given
    file_content = b"invalid content"
    filename = "test.txt"
    doc_id = UUID('12345678-1234-5678-1234-567812345678')
    mock_storage.save_document.return_value = doc_id
    
    with patch('processing.processor.partition', side_effect=Exception("Extraction failed")):
        # When/Then
        with pytest.raises(Exception) as exc_info:
            await processor.process_document(file_content, filename)
        
        assert "Document processing failed" in str(exc_info.value)
        mock_storage.metadata.update_document_status.assert_called_with(
            doc_id,
            DocumentStatus.FAILED.value
        )
        mock_storage.delete_document.assert_called_once_with(doc_id)

@pytest.mark.asyncio
async def test_create_chunks_valid_content(processor):
    # Given
    text = "This is a test document that needs to be split into chunks. " * 10
    doc_id = UUID('12345678-1234-5678-1234-567812345678')
    
    # When
    chunks = await processor._create_chunks(text, doc_id)
    
    # Then
    assert len(chunks) > 0
    assert all(len(chunk.strip()) >= processor.config.min_chunk_size for chunk in chunks)
    assert isinstance(chunks[0], str)

@pytest.mark.asyncio
async def test_create_chunks_small_content(processor):
    # Given
    text = "Small text"
    doc_id = UUID('12345678-1234-5678-1234-567812345678')
    
    # When
    chunks = await processor._create_chunks(text, doc_id)
    
    # Then
    assert len(chunks) == 1
    assert chunks[0] == text

@pytest.mark.asyncio
@pytest.mark.skip("Not implemented")
async def test_generate_embeddings(processor, mock_openai):
    # Given
    chunks = ["test chunk 1", "test chunk 2"]
    doc_id = UUID('12345678-1234-5678-1234-567812345678')
    
    # When
    embeddings = await processor._generate_embeddings(chunks, doc_id)
    
    # Then
    assert len(embeddings) == len(chunks)
    assert all(isinstance(emb, list) for emb in embeddings)
    mock_openai.embeddings.create.assert_called_once()

@pytest.mark.asyncio
async def test_cleanup_on_failure(processor, mock_storage):
    # Given
    file_content = b"Test content"
    filename = "test.txt"
    doc_id = UUID('12345678-1234-5678-1234-567812345678')
    mock_storage.save_document.return_value = doc_id
    mock_storage.save_processed_chunks.side_effect = Exception("Storage error")
    
    # When/Then
    with pytest.raises(ProcessingError):
        await processor.process_document(file_content, filename)
    
    mock_storage.metadata.update_document_status.assert_called_with(
        doc_id,
        DocumentStatus.FAILED.value
    )
    mock_storage.delete_document.assert_called_once_with(doc_id)
