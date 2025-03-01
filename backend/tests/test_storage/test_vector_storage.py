import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4, UUID
from backend.storage.vector_storage import VectorStorage
from backend.storage.storage_interface import ChunkMetadata

@pytest.mark.asyncio
@patch("backend.storage.vector_storage.Client")
@patch("backend.storage.vector_storage.Settings")
async def test_add_chunks(mock_settings, mock_client):
    # Given
    doc_id = uuid4()
    chunk_id = uuid4()
    chunk = ChunkMetadata(
        id=chunk_id,
        document_id=doc_id,
        sequence=0,
        content="Test chunk",
        embedding_id=str(chunk_id)
    )
    chunks = [chunk]
    embeddings = [[0.1, 0.2, 0.3]]
    
    mock_collection = AsyncMock()
    mock_client.return_value.get_or_create_collection.return_value = mock_collection
    
    vector_storage = VectorStorage(persist_dir="test_dir")
    
    # When
    await vector_storage.add_chunks(chunks, embeddings)
    
    # Then
    mock_collection.add.assert_called_once_with(
        ids=[str(chunk_id)],
        embeddings=embeddings,
        metadatas=[{
            "document_id": str(doc_id),
            "sequence": chunk.sequence
        }],
        documents=[chunk.content]
    )

@pytest.mark.asyncio
@patch("backend.storage.vector_storage.Client")
@patch("backend.storage.vector_storage.Settings")
async def test_search(mock_settings, mock_client):
    # Given
    query_embedding = [0.1, 0.2, 0.3]
    limit = 5

    mock_collection = AsyncMock()
    mock_client.return_value.get_or_create_collection.return_value = mock_collection
    
    mock_collection.query.return_value = [
        {"id": "123", "metadata": {"document_id": "doc_id_1", "sequence": 0}, "document": "Chunk 1"},
        {"id": "124", "metadata": {"document_id": "doc_id_2", "sequence": 1}, "document": "Chunk 2"}
    ]
    
    vector_storage = VectorStorage(persist_dir="test_dir")
    
    # When
    results = await (await vector_storage.search(query_embedding, limit))
    
    # Then
    mock_collection.query.assert_called_once_with(
        query_embeddings=[query_embedding],
        n_results=limit,
        include=["metadatas", "documents", "distances"]
    )
    
    # Make sure the results are correct after awaiting
    assert len(results) == 2
    assert results[0]["id"] == "123"
    assert results[1]["id"] == "124"

@pytest.mark.asyncio
@patch("backend.storage.vector_storage.Client")
@patch("backend.storage.vector_storage.Settings")
async def test_delete_chunks(mock_settings, mock_client):
    # Given
    doc_id_1 = uuid4()
    chunk_id_1 = uuid4()
    
    chunk_1 = ChunkMetadata(
        id=doc_id_1,
        document_id=chunk_id_1,
        sequence=0,
        content="Test chunk",
        embedding_id=str(chunk_id_1)
    )
    
    doc_id_2 = uuid4()
    chunk_id_2 = uuid4()
    
    chunk_2 = ChunkMetadata(
        id=doc_id_2,
        document_id=chunk_id_2,
        sequence=0,
        content="Test chunk",
        embedding_id=str(chunk_id_2)
    )

    mock_collection = AsyncMock()
    mock_collection.delete = AsyncMock()
    mock_client.return_value.get_or_create_collection.return_value = mock_collection
    
    vector_storage = VectorStorage(persist_dir="test_dir")
    vector_storage.get_chunks_by_document_id = AsyncMock(return_value=[chunk_1])
    
    # When
    await vector_storage.delete_chunks(doc_id_1)
    
    # Then
    mock_collection.delete.assert_called_once_with(ids=[str(chunk_1.id)])

@pytest.mark.asyncio
@patch("backend.storage.vector_storage.Client")
@patch("backend.storage.vector_storage.Settings")
async def test_get_chunks_by_document_id(mock_settings, mock_client):
    # Given
    doc_id = uuid4()
    chunk_id_1 = uuid4()
    chunk_id_2 = uuid4()
    
    mock_collection = AsyncMock()
    mock_client.return_value.get_or_create_collection.return_value = mock_collection
    mock_collection.query.return_value = [
        {"id": str(chunk_id_1), "metadata": {"document_id": str(doc_id), "sequence": 0}, "document": "Chunk 1"},
        {"id": str(chunk_id_2), "metadata": {"document_id": str(doc_id), "sequence": 1}, "document": "Chunk 2"}
    ]
    
    vector_storage = VectorStorage(persist_dir="test_dir")
    
    # When
    chunks = await vector_storage.get_chunks_by_document_id(doc_id)
    
    # Then
    mock_collection.query.assert_called_once_with(
        query_filter={"document_id": str(doc_id)},
        include=["metadatas", "documents"]
    )
    assert len(chunks) == 2
    assert chunks[0].id == chunk_id_1
    assert chunks[1].id == chunk_id_2
    assert chunks[0].content == "Chunk 1"
