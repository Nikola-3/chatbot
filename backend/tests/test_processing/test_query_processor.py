import pytest
from unittest.mock import Mock, AsyncMock
from uuid import UUID

from backend.processing.query_processor import QueryProcessor
from backend.processing.config import ProcessingConfig
from backend.processing.exceptions import EmbeddingError
from backend.storage.storage_manager import StorageManager
from backend.storage.storage_interface import ChunkMetadata

@pytest.fixture
def mock_storage():
    storage = Mock(spec=StorageManager)
    storage.vectors = AsyncMock()
    return storage

@pytest.fixture
def mock_openai():
    client = AsyncMock()
    client.embeddings.create = AsyncMock()
    return client

@pytest.fixture
def config():
    return ProcessingConfig()

@pytest.fixture
def processor(mock_storage, mock_openai, config):
    return QueryProcessor(mock_storage, mock_openai, config)

@pytest.mark.asyncio
@pytest.mark.skip("Not implemented")
async def test_generate_embedding(processor, mock_openai):
    # Given
    expected_embedding = [0.1, 0.2, 0.3]
    mock_openai.embeddings.create.return_value.data = [
        Mock(embedding=expected_embedding)
    ]

    # When
    result = await processor._generate_embedding("test text")

    # Then
    assert result == expected_embedding
    mock_openai.embeddings.create.assert_called_once_with(
        model=processor.config.embedding_model,
        input=["test text"]
    )

@pytest.mark.asyncio
@pytest.mark.skip("Not implemented")
async def test_generate_embedding_error(processor, mock_openai):
    # Given
    mock_openai.embeddings.create.side_effect = Exception("API error")

    # When / Then
    with pytest.raises(EmbeddingError):
        await processor._generate_embedding("Failed to generate query embedding: API error")

def test_format_context(processor):
    # Given
    chunks = [
        {"content": "First chunk"},
        {"content": "Second chunk"},
        {"content": "Third chunk"}
    ]

    # When
    result = processor._format_context(chunks)

    # Then
    expected = "[1] First chunk\n\n[2] Second chunk\n\n[3] Third chunk"
    assert result == expected

@pytest.mark.asyncio
async def test_get_relevant_chunks(processor, mock_storage):
    # Given
    mock_search_results = {
        'ids': [[str(UUID(int=1)), str(UUID(int=2))]],
        'documents': [["content1", "content2"]],
        'metadatas': [[
            {'document_id': str(UUID(int=10)), 'sequence': 1},
            {'document_id': str(UUID(int=11)), 'sequence': 2}
        ]]
    }
    mock_storage.vectors.search.return_value = mock_search_results

    # When
    result = await processor.get_relevant_chunks([0.1, 0.2, 0.3], limit=2)

    # Then
    assert len(result) == 2
    assert str(result[0].document_id) == str(UUID(int=10))
    assert result[0].sequence == 1
    assert result[0].content == "content1"

@pytest.mark.asyncio
@pytest.mark.skip("Not implemented")
async def test_process_query(processor):
    # Given
    query = "test query"
    embedding = [0.1, 0.2, 0.3]
    chunks = [
        ChunkMetadata(
            id=UUID(int=1),
            document_id=UUID(int=10),
            sequence=1,
            content="relevant content",
            embedding_id=str(UUID(int=1))
        )
    ]

    processor._generate_embedding = AsyncMock(return_value=embedding)
    processor.get_relevant_chunks = AsyncMock(return_value=chunks)

    # When
    result = await processor.process_query(query, limit=1)

    # Then
    assert result["query"] == query
    assert result["chunks"] is not None
    assert isinstance(result["context"], str)
    processor._generate_embedding.assert_called_once_with(query)
    processor.get_relevant_chunks.assert_called_once_with(embedding, limit=1)
