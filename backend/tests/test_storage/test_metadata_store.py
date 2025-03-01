import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from backend.storage.metadata_store import MetadataStore
from backend.storage.storage_interface import DocumentMetadata, ChunkMetadata


@pytest.mark.asyncio
@patch("storage.metadata_store.create_async_engine")
@patch("storage.metadata_store.async_sessionmaker")
async def test_save_document_metadata(mock_sessionmaker, mock_create_engine):
    # Given
    mock_session = AsyncMock()
    mock_sessionmaker.return_value = mock_session

    metadata = DocumentMetadata(id=uuid4(), filename="test.pdf", mime_type="application/pdf", size_bytes=1024)
    
    metadata_store = MetadataStore(db_url="sqlite+aiosqlite:///:memory:")
    # When
    await metadata_store.save_document_metadata(metadata)
    # Then
    mock_session.add.assert_called_once_with(metadata)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch("storage.metadata_store.create_async_engine")
@patch("storage.metadata_store.async_sessionmaker")
async def test_save_document_metadata_failure(mock_sessionmaker, mock_create_engine):
    # Given
    mock_session = AsyncMock()
    mock_sessionmaker.return_value = mock_session

    metadata = DocumentMetadata(id=uuid4(), filename="test.pdf", mime_type="application/pdf", size_bytes=1024)
    mock_session.commit.side_effect = Exception("Database error")
    
    metadata_store = MetadataStore(db_url="sqlite+aiosqlite:///:memory:")

    # When
    with pytest.raises(Exception):
        await metadata_store.save_document_metadata(metadata)

    # Then
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
@patch("storage.metadata_store.create_async_engine")
@patch("storage.metadata_store.async_sessionmaker")
async def test_save_chunks(mock_sessionmaker, mock_create_engine):
    # Given
    mock_session = AsyncMock()
    mock_sessionmaker.return_value = mock_session

    chunks = [ChunkMetadata(id=uuid4(), document_id=uuid4(), sequence=i, content="chunk content", embedding_id=str(i)) for i in range(3)]
    
    metadata_store = MetadataStore(db_url="sqlite+aiosqlite:///:memory:")

    # When
    await metadata_store.save_chunks(chunks)

    # Then
    for chunk in chunks:
        mock_session.add.assert_called_with(chunk)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch("storage.metadata_store.create_async_engine")
@patch("storage.metadata_store.async_sessionmaker")
async def test_save_chunks_failure(mock_sessionmaker, mock_create_engine):
    # Given
    mock_session = AsyncMock()
    mock_sessionmaker.return_value = mock_session

    chunks = [ChunkMetadata(id=uuid4(), document_id=uuid4(), sequence=i, content="chunk content", embedding_id=str(i)) for i in range(3)]
    mock_session.commit.side_effect = Exception("Database error")
    
    metadata_store = MetadataStore(db_url="sqlite+aiosqlite:///:memory:")

    # When
    with pytest.raises(Exception):
        await metadata_store.save_chunks(chunks)

    # Then
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
@patch("storage.metadata_store.create_async_engine")
@patch("storage.metadata_store.async_sessionmaker")
async def test_update_document_status(mock_sessionmaker, mock_create_engine):
    # Given
    doc_id = uuid4()
    status = "processed"
    mock_session = AsyncMock()
    mock_sessionmaker.return_value = mock_session

    doc = DocumentMetadata(id=doc_id, filename="test.pdf", mime_type="application/pdf", size_bytes=1024)
    mock_session.get = AsyncMock(return_value=doc)
    
    metadata_store = MetadataStore(db_url="sqlite+aiosqlite:///:memory:")

    # When
    await metadata_store.update_document_status(doc_id, status)

    # Then
    mock_session.get.assert_called_once_with(DocumentMetadata, doc_id)
    assert doc.status == status
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch("storage.metadata_store.create_async_engine")
@patch("storage.metadata_store.async_sessionmaker")
async def test_update_document_status_document_not_found(mock_sessionmaker, mock_create_engine):
    # Given
    doc_id = uuid4()
    status = "processed"
    mock_session = AsyncMock()
    mock_sessionmaker.return_value = mock_session

    mock_session.get = AsyncMock(return_value=None)
    
    metadata_store = MetadataStore(db_url="sqlite+aiosqlite:///:memory:")

    # When
    with pytest.raises(ValueError, match=f"Document {doc_id} not found."):
        await metadata_store.update_document_status(doc_id, status)

    # Then
    mock_session.get.assert_called_once_with(DocumentMetadata, doc_id)
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
@patch("storage.metadata_store.create_async_engine")
@patch("storage.metadata_store.async_sessionmaker")
async def test_delete_document_metadata(mock_sessionmaker, mock_create_engine):
    # Given
    doc_id = uuid4()
    mock_session = AsyncMock()
    mock_sessionmaker.return_value = mock_session

    doc = DocumentMetadata(id=doc_id, filename="test.pdf", mime_type="application/pdf", size_bytes=1024)
    mock_session.get = AsyncMock(return_value=doc)

    metadata_store = MetadataStore(db_url="sqlite+aiosqlite:///:memory:")

    # When
    await metadata_store.delete_document_metadata(doc_id)

    # Then
    mock_session.delete.assert_called_once_with(doc)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch("storage.metadata_store.create_async_engine")
@patch("storage.metadata_store.async_sessionmaker")
async def test_delete_document_metadata_document_not_found(mock_sessionmaker, mock_create_engine):
    # Given
    doc_id = uuid4()
    mock_session = AsyncMock()
    mock_sessionmaker.return_value = mock_session

    mock_session.get = AsyncMock(return_value=None)

    metadata_store = MetadataStore(db_url="sqlite+aiosqlite:///:memory:")

    # When
    with pytest.raises(ValueError, match=f"Document {doc_id} not found."):
        await metadata_store.delete_document_metadata(doc_id)

    # Then
    mock_session.get.assert_called_once_with(DocumentMetadata, doc_id)
    mock_session.rollback.assert_called_once()


@pytest.mark.asyncio
@patch("storage.metadata_store.create_async_engine")
@patch("storage.metadata_store.async_sessionmaker")
async def test_delete_chunks(mock_sessionmaker, mock_create_engine):
    # Given
    doc_id = uuid4()
    mock_session = AsyncMock()
    mock_sessionmaker.return_value = mock_session

    mock_session.execute = AsyncMock(return_value=MagicMock(rowcount=2))

    metadata_store = MetadataStore(db_url="sqlite+aiosqlite:///:memory:")

    # When
    await metadata_store.delete_chunks(doc_id)

    # Then
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
@patch("storage.metadata_store.create_async_engine")
@patch("storage.metadata_store.async_sessionmaker")
async def test_delete_chunks_no_chunks(mock_sessionmaker, mock_create_engine):
    # Given
    doc_id = uuid4()
    mock_session = AsyncMock()
    mock_sessionmaker.return_value = mock_session

    mock_session.execute = AsyncMock(return_value=MagicMock(rowcount=0))

    metadata_store = MetadataStore(db_url="sqlite+aiosqlite:///:memory:")

    # When
    with pytest.raises(ValueError, match=f"No chunks found for document {doc_id}."):
        await metadata_store.delete_chunks(doc_id)

    # Then
    mock_session.execute.assert_called_once()
    mock_session.rollback.assert_called_once()
