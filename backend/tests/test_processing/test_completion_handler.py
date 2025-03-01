import pytest
from unittest.mock import Mock, AsyncMock, patch
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from processing.completion_handler import CompletionHandler
from processing.prompt_manager import PromptManager
from processing.query_processor import QueryProcessor

@pytest.fixture
def mock_query_processor():
    processor = Mock(spec=QueryProcessor)
    processor.process_query = AsyncMock(return_value={
        "query": "test question",
        "chunks": [],
        "context": "test context"
    })
    return processor

@pytest.fixture
def mock_openai():
    client = AsyncMock()
    mock_completion = ChatCompletion(
        id="test-id",
        model="gpt-3.5-turbo",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="Test response",
                    role="assistant"
                )
            )
        ],
        created=1234567890,
        object="chat.completion"
    )
    client.chat.completions.create = AsyncMock(return_value=mock_completion)
    return client

@pytest.fixture
def completion_handler(mock_query_processor, mock_openai):
    prompt_manager = PromptManager()
    return CompletionHandler(
        query_processor=mock_query_processor,
        prompt_manager=prompt_manager,
        openai_client=mock_openai
    )

@pytest.mark.asyncio
async def test_get_response_without_conversation(completion_handler, mock_openai):
    # When
    result = await completion_handler.get_response("test question")
    
    # Then
    assert result["answer"] == "Test response"
    assert result["context"] == "test context"
    assert result["chunks"] == []
    assert result["conversation_history"] == []
    
    mock_openai.chat.completions.create.assert_called_once()

@pytest.mark.asyncio
async def test_get_response_with_conversation(completion_handler, mock_openai):
    # Given
    conversation_id = "test-conv-1"
    question = "test question"
    
    # When
    result = await completion_handler.get_response(
        question=question,
        conversation_id=conversation_id
    )
    
    # Then
    assert len(result["conversation_history"]) == 2
    assert result["conversation_history"][0]["role"] == "user"
    assert result["conversation_history"][0]["content"] == question
    assert result["conversation_history"][1]["role"] == "assistant"
    assert result["conversation_history"][1]["content"] == "Test response"

@pytest.mark.asyncio
async def test_get_response_with_existing_history(completion_handler):
    # Given
    conversation_id = "test-conv-2"
    existing_history = [
        {"role": "user", "content": "previous question"},
        {"role": "assistant", "content": "previous answer"}
    ]
    completion_handler.conversation_manager.update_history(
        conversation_id,
        existing_history
    )
    
    # When
    result = await completion_handler.get_response(
        question="new question",
        conversation_id=conversation_id
    )
    
    # Then
    assert len(result["conversation_history"]) == 4
    assert result["conversation_history"][0]["content"] == "previous question"
    assert result["conversation_history"][-2]["content"] == "new question"

@pytest.mark.asyncio
async def test_get_response_error_handling(completion_handler, mock_openai):
    # Given
    mock_openai.chat.completions.create.side_effect = Exception("API error")
    
    # Then
    with pytest.raises(Exception) as exc_info:
        await completion_handler.get_response("test question")
    assert "Failed to get completion" in str(exc_info.value)

def test_update_history_creates_new_history_if_none_exists(completion_handler):
    # Given
    mock_completion = Mock()
    mock_choice = Mock()
    mock_choice.message.content = "test response"
    mock_completion.choices = [mock_choice]
    
    # When
    history = completion_handler.update_history(
        "test question",
        "conv-id",
        None,
        mock_completion
    )
    
    # Then
    assert len(history) == 2
    assert history[0]["content"] == "test question"
    assert history[1]["content"] == "test response"
