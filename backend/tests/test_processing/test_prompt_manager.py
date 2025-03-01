import pytest
from processing.prompt_manager import PromptManager

@pytest.fixture
def prompt_manager():
    return PromptManager()

@pytest.fixture
def custom_template():
    return """Custom template:
Question: {question}
Available context: {context}
Please respond:"""

def test_default_template_initialization(prompt_manager):
    assert prompt_manager.template == PromptManager.DEFAULT_TEMPLATE

def test_custom_template_initialization():
    custom_prompt_manager = PromptManager(template="Custom: {question} Context: {context}")
    assert custom_prompt_manager.template == "Custom: {question} Context: {context}"

def test_create_prompt(prompt_manager):
    # Given
    question = "What is the capital of France?"
    context = "France is a country in Europe. Its capital is Paris."
    
    # When
    result = prompt_manager.create_prompt(question, context)
    
    # Then
    assert question in result
    assert context in result
    assert "Use the following context" in result
    assert "Question:" in result
    assert "Answer:" in result

def test_create_chat_messages_without_history(prompt_manager):
    # Given
    question = "Test question"
    context = "Test context"
    
    # When
    messages = prompt_manager.create_chat_messages(question, context)
    
    # Then
    assert len(messages) == 2  # System message + user message
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "Test question" in messages[1]["content"]
    assert "Test context" in messages[1]["content"]

def test_create_chat_messages_with_history(prompt_manager):
    # Given
    question = "Follow-up question"
    context = "Relevant context"
    history = [
        {"role": "user", "content": "Initial question"},
        {"role": "assistant", "content": "Initial answer"}
    ]
    
    # When
    messages = prompt_manager.create_chat_messages(question, context, history)
    
    # Then
    assert len(messages) == 4  # System + 2 history + current question
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"
    assert messages[3]["role"] == "user"
    assert "Follow-up question" in messages[3]["content"]

def test_create_prompt_with_empty_context(prompt_manager):
    # Given
    question = "Test question"
    context = ""
    
    # When
    result = prompt_manager.create_prompt(question, context)
    
    # Then
    assert question in result
    assert "Context:" in result

def test_create_chat_messages_with_empty_history(prompt_manager):
    # Given
    question = "Test question"
    context = "Test context"
    history = []
    
    # When
    messages = prompt_manager.create_chat_messages(question, context, history)
    
    # Then
    assert len(messages) == 2  # Should only have system and user message
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
