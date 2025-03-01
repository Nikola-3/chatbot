import pytest
from datetime import datetime, timedelta
from processing.conversation import ConversationManager
import time
import asyncio

@pytest.fixture
def conversation_manager():
    """Create manager with very short expiry for testing
    expiry_minutes=0.1 means 6 seconds
    cleanup_interval=0.05 means 3 seconds
    """
    return ConversationManager(
        max_history=3,
        expiry_minutes=0.075,  # 6 seconds
        cleanup_interval=0.05  # 3 seconds
    )

def test_get_history_nonexistent(conversation_manager):
    # Given / When
    history = conversation_manager.get_history("nonexistent_id")
    
    # Then
    assert history is None

def test_update_and_get_history(conversation_manager):
    # Given
    conv_id = "test_conv_1"
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"}
    ]
    
    # When
    conversation_manager.update_history(conv_id, messages)
    
    # Get and verify history
    history = conversation_manager.get_history(conv_id)
    assert history == messages
    assert conv_id in conversation_manager.last_accessed

def test_max_history_limit(conversation_manager):
    # Given
    conv_id = "test_conv_2"
    messages = [
        {"role": "user", "content": f"Message {i}"}
        for i in range(5)  # More than max_history (3)
    ]
    
    # When
    conversation_manager.update_history(conv_id, messages)
    history = conversation_manager.get_history(conv_id)
    
    # Then
    assert len(history) == 3
    assert history[-1]["content"] == "Message 4"

@pytest.mark.asyncio
async def test_conversation_expiry(conversation_manager):
    """Test that conversations expire after the configured time
    Wait time is 0.15 minutes (9 seconds), which is longer than
    expiry_minutes (0.1 = 6 seconds)
    """
    # Given
    conv_id = "test_conv_3"
    messages = [{"role": "user", "content": "Test message"}]
    
    # When
    conversation_manager.update_history(conv_id, messages)
    
    # Wait for expiry (9 seconds > 6 seconds expiry time)
    await asyncio.sleep(0.1)
    
    # Verify conversation was cleaned up
    history = conversation_manager.get_history(conv_id)

    assert conv_id not in conversation_manager.conversations
    assert conv_id not in conversation_manager.last_accessed

def test_last_accessed_updates(conversation_manager):
    # Given
    conv_id = "test_conv_4"
    messages = [{"role": "user", "content": "Test message"}]
    
    # When
    conversation_manager.update_history(conv_id, messages)
    first_access = conversation_manager.last_accessed[conv_id]
    
    # Wait briefly
    time.sleep(0.1)
    
    # Get history and check last_accessed was updated
    conversation_manager.get_history(conv_id)
    second_access = conversation_manager.last_accessed[conv_id]
    
    # Then
    assert second_access > first_access

def test_cleanup_expired_conversations(conversation_manager):
    # Given
    conv_id = "test_conv_5"
    messages = [{"role": "user", "content": "Test message"}]
    
    # When
    conversation_manager.update_history(conv_id, messages)
    
    # Manually set last_accessed to an expired time
    conversation_manager.last_accessed[conv_id] = datetime.now() - timedelta(minutes=2)
    
    # Trigger cleanup manually
    conversation_manager._cleanup_expired()
    
    # Then
    assert conv_id not in conversation_manager.conversations
    assert conv_id not in conversation_manager.last_accessed
