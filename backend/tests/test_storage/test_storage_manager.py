import pytest
from unittest.mock import AsyncMock, patch
from uuid import UUID
from backend.storage.storage_manager import StorageManager
from backend.storage.storage_interface import DocumentMetadata, ChunkMetadata

STORAGE_MANAGER: str = "backend.storage.storage_manager"

@pytest.fixture
def setup_storage_manager():
    
    with patch(STORAGE_MANAGER + ".FileSystemStorage") as MockFileSystemStorage, \
         patch(STORAGE_MANAGER + ".VectorStorage") as MockVectorStorage, \
         patch(STORAGE_MANAGER + ".MetadataStore") as MockMetadataStore:

        
        mock_file_storage = MockFileSystemStorage()
        mock_vector_storage = MockVectorStorage()
        mock_metadata_storage = MockMetadataStore()

        storage_manager = StorageManager(
            file_storage=mock_file_storage,
            vector_storage=mock_vector_storage,
            metadata_storage=mock_metadata_storage
        )

        yield storage_manager, mock_file_storage, mock_vector_storage, mock_metadata_storage


@pytest.mark.asyncio
@patch("magic.Magic.from_buffer")
@patch("backend.storage.storage_manager.uuid4")
async def test_save_document(mock_uuid, mock_mime, setup_storage_manager):
    
    # Given
    content = b"test content"
    filename = "test.pdf"
    doc_id = UUID("12345678-1234-5678-1234-567812345678")
    
    mock_mime.return_value = "application/pdf"
    mock_uuid.return_value = doc_id

    storage_manager, mock_file_storage, mock_vector_storage, mock_metadata_storage = setup_storage_manager

    mock_file_storage.save_document = AsyncMock(return_value=doc_id)
    mock_metadata_storage.save_document_metadata = AsyncMock(return_value=doc_id)

    # When    
    result = await storage_manager.save_document(content, filename)

    # Then
    mock_file_storage.save_document.assert_called_once_with(content, DocumentMetadata(
        id=doc_id,
        filename=filename,
        mime_type="application/pdf",
        size_bytes=len(content)
    ))
    mock_metadata_storage.save_document_metadata.assert_called_once()
    assert result == doc_id


@pytest.mark.asyncio
@patch("magic.Magic.from_buffer")
async def test_save_document_failure(mock_mime, setup_storage_manager):
    # Given
    content = b"test content"
    filename = "test.pdf"
    
    mock_mime.return_value = "application/pdf"
    
    storage_manager, mock_file_storage, mock_vector_storage, mock_metadata_storage = setup_storage_manager

    mock_file_storage.save_document = AsyncMock(side_effect=Exception("Save failed"))
    
    # When / Then
    with pytest.raises(Exception):
        await storage_manager.save_document(content, filename)


@pytest.mark.asyncio
async def test_save_processed_chunks(setup_storage_manager):
    # Given
    doc_id = UUID("12345678-1234-5678-1234-567812345678")
    chunks = [ChunkMetadata(id=UUID("12345678-1234-5678-1234-567812345679"), document_id=doc_id, sequence=0, content="chunk1", embedding_id="abc")]
    embeddings = [[0.1, 0.2, 0.3]]
    
    storage_manager, mock_file_storage, mock_vector_storage, mock_metadata_storage = setup_storage_manager

    mock_metadata_storage.save_chunks = AsyncMock(return_value=None)
    mock_vector_storage.add_chunks = AsyncMock(return_value=None)
    mock_metadata_storage.update_document_status = AsyncMock(return_value=None)
    
    # When
    await storage_manager.save_processed_chunks(doc_id, chunks, embeddings)
    
    # Then
    mock_metadata_storage.save_chunks.assert_called_once_with(chunks)
    mock_vector_storage.add_chunks.assert_called_once_with(chunks, embeddings)
    mock_metadata_storage.update_document_status.assert_called_with(doc_id, "processed")
    mock_metadata_storage.update_document_status.call_count == 2


@pytest.mark.asyncio
async def test_save_processed_chunks_failure(setup_storage_manager):
    # Given
    doc_id = UUID("12345678-1234-5678-1234-567812345678")
    chunks = [ChunkMetadata(id=UUID("12345678-1234-5678-1234-567812345679"), document_id=doc_id, content="chunk1", sequence=0, embedding_id="abc")]
    embeddings = [[0.1, 0.2, 0.3]]
    
    storage_manager, mock_file_storage, mock_vector_storage, mock_metadata_storage = setup_storage_manager

    mock_metadata_storage.save_chunks = AsyncMock(side_effect=Exception("Save chunks failed"))
    
    # When / Then
    with pytest.raises(Exception):
        await storage_manager.save_processed_chunks(doc_id, chunks, embeddings)


@pytest.mark.asyncio
async def test_delete_document(setup_storage_manager):
    # Given
    doc_id = UUID("12345678-1234-5678-1234-567812345678")
    
    storage_manager, mock_file_storage, mock_vector_storage, mock_metadata_storage = setup_storage_manager

    mock_file_storage.delete_document = AsyncMock(return_value=True)
    mock_metadata_storage.delete_document_metadata = AsyncMock(return_value=None)
    mock_metadata_storage.delete_chunks = AsyncMock(return_value=None)
    mock_vector_storage.delete_chunks = AsyncMock(return_value=None)
    
    # When
    file_deleted = await storage_manager.delete_document(doc_id)
    
    # Then
    mock_file_storage.delete_document.assert_called_once_with(doc_id)
    mock_metadata_storage.delete_document_metadata.assert_called_once_with(doc_id)
    mock_metadata_storage.delete_chunks.assert_called_once_with(doc_id)
    mock_vector_storage.delete_chunks.assert_called_once_with(doc_id)
    assert file_deleted is True


@pytest.mark.asyncio
async def test_delete_document_failure(setup_storage_manager):
    # Given
    doc_id = UUID("12345678-1234-5678-1234-567812345678")
    
    storage_manager, mock_file_storage, mock_vector_storage, mock_metadata_storage = setup_storage_manager

    mock_file_storage.delete_document = AsyncMock(side_effect=Exception("Delete failed"))
    
    # When / Then
    with pytest.raises(Exception):
        await storage_manager.delete_document(doc_id)
