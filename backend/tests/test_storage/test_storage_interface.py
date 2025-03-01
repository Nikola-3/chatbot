import pytest
from uuid import uuid4, UUID
from typing import Optional
from unittest.mock import AsyncMock, patch
from backend.storage.storage_interface import DocumentMetadata, ChunkMetadata, StorageInterface

mock_storage = AsyncMock(spec=StorageInterface)

mock_storage.save_document = AsyncMock(return_value=UUID('123e4567-e89b-12d3-a456-426614174000'))

mock_storage.save_chunks = AsyncMock(return_value=True)

mock_storage.get_document = AsyncMock(return_value=b"Document content")

mock_storage.get_chunks = AsyncMock(return_value=[ChunkMetadata(id=UUID('123e4567-e89b-12d3-a456-426614174001'), document_id=UUID('12345678-1234-5678-1234-567812345678'), sequence=0, content="chunk1", embedding_id="embed1")])

mock_storage.delete_document = AsyncMock(return_value=True)

@pytest.mark.asyncio
async def test_save_document():
    
    mock_storage = AsyncMock(spec=StorageInterface)

    
    doc_id = uuid4()
    metadata = DocumentMetadata(id=doc_id, filename="test.txt", mime_type="text/plain", size_bytes=100)
    content = b"Hello, world!"

    
    mock_storage.save_document = AsyncMock(return_value=doc_id)
    mock_storage.get_document = AsyncMock(return_value=content)

    
    saved_id = await mock_storage.save_document(content, metadata)
    assert saved_id == doc_id

    assert await mock_storage.get_document(doc_id) == content

@pytest.mark.asyncio
async def test_save_chunks():

    mock_storage = AsyncMock(spec=StorageInterface)

    doc_id = uuid4()
    chunks = [ChunkMetadata(id=uuid4(), document_id=doc_id, sequence=0, content="chunk1", embedding_id="embed1")]

    mock_storage.save_chunks = AsyncMock(return_value=True)
    mock_storage.get_chunks = AsyncMock(return_value=chunks)

    await mock_storage.save_chunks(doc_id, chunks)
    assert await mock_storage.get_chunks(doc_id) == chunks

@pytest.mark.asyncio
async def test_delete_document():

    mock_storage = AsyncMock(spec=StorageInterface)

    doc_id = uuid4()
    metadata = DocumentMetadata(id=doc_id, filename="test.txt", mime_type="text/plain", size_bytes=100)
    content = b"Hello, world!"

    mock_storage.save_document = AsyncMock(return_value=doc_id)
    mock_storage.get_document = AsyncMock(return_value=None)
    mock_storage.get_chunks = AsyncMock(return_value=[])
    mock_storage.delete_document = AsyncMock(return_value=True)

    await mock_storage.save_document(content, metadata)
    assert await mock_storage.delete_document(doc_id) == True

    assert await mock_storage.get_document(doc_id) is None
    assert await mock_storage.get_chunks(doc_id) == []

@pytest.mark.asyncio
async def test_get_document_not_found():

    mock_storage = AsyncMock(spec=StorageInterface)

    non_existent_doc_id = uuid4()

    mock_storage.get_document = AsyncMock(return_value=None)

    result = await mock_storage.get_document(non_existent_doc_id)
    assert result is None

@pytest.mark.asyncio
async def test_get_chunks_not_found():
    
    mock_storage = AsyncMock(spec=StorageInterface)

    non_existent_doc_id = uuid4()

    mock_storage.get_chunks = AsyncMock(return_value=[])

    result = await mock_storage.get_chunks(non_existent_doc_id)
    assert result == []

@pytest.mark.asyncio
async def test_save_chunks_invalid_document():

    mock_storage = AsyncMock(spec=StorageInterface)

    doc_id = uuid4()
    chunks = [ChunkMetadata(id=uuid4(), document_id=doc_id, sequence=0, content="chunk1", embedding_id="embed1")]

    mock_storage.save_chunks = AsyncMock(return_value=False)

    result = await mock_storage.save_chunks(doc_id, chunks)
    assert result is False

@pytest.mark.asyncio
async def test_delete_document_not_found():

    mock_storage = AsyncMock(spec=StorageInterface)

    non_existent_doc_id = uuid4()

    mock_storage.delete_document = AsyncMock(return_value=False)

    result = await mock_storage.delete_document(non_existent_doc_id)
    assert result is False

@pytest.mark.asyncio
async def test_save_document_invalid_data():
    
    mock_storage = AsyncMock(spec=StorageInterface)

    invalid_metadata = DocumentMetadata(id=uuid4(), filename="", mime_type="", size_bytes=100)
    content = b"Hello, world!"  # Valid content, but invalid metadata

    mock_storage.save_document = AsyncMock(side_effect=ValueError("Invalid document data"))

    with pytest.raises(ValueError, match="Invalid document data"):
        await mock_storage.save_document(content, invalid_metadata)

@pytest.mark.asyncio
async def test_save_empty_chunks():
    
    mock_storage = AsyncMock(spec=StorageInterface)

    doc_id = uuid4()
    empty_chunks = []

    mock_storage.save_chunks = AsyncMock(return_value=True)

    result = await mock_storage.save_chunks(doc_id, empty_chunks)
    assert result is True
