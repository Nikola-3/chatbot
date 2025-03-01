from typing import Optional
from openai import AsyncOpenAI

from .query_processor import QueryProcessor
from .prompt_manager import PromptManager
from .exceptions import ProcessingError
from .conversation import ConversationManager

class CompletionHandler:
    def __init__(
        self,
        query_processor: QueryProcessor,
        prompt_manager: PromptManager,
        openai_client: AsyncOpenAI,
        model: str = "gpt-3.5-turbo",
        max_history: int = 20
    ):
        self.query_processor = query_processor
        self.prompt_manager = prompt_manager
        self.openai = openai_client
        self.model = model
        self.conversation_manager = ConversationManager(max_history=max_history)

    async def get_response(
        self,
        question: str,
        context_limit: int = 3,
        conversation_id: Optional[str] = None
    ) -> dict[str, any]:
        """Process a question and get an AI response using relevant context"""
        try:
            
            conversation_history = None
            if conversation_id:
                conversation_history = self.conversation_manager.get_history(conversation_id)

            query_result = await self.query_processor.process_query(
                query=question,
                limit=context_limit
            )

            messages = self.prompt_manager.create_chat_messages(
                question=question,
                context=query_result["context"],
                history=conversation_history
            )

            completion = await self.openai.chat.completions.create(
                model=self.model,
                messages=messages
            )

            
            conversation_history = self.update_history(question, conversation_id, conversation_history, completion)

            return {
                "answer": completion.choices[0].message.content,
                "context": query_result["context"],
                "chunks": query_result["chunks"],
                "conversation_history": conversation_history or []
            }

        except Exception as e:
            raise ProcessingError(f"Failed to get completion: {str(e)}") from e

    def update_history(self, question, conversation_id, conversation_history, completion):
        if conversation_id:
            if conversation_history is None:
                conversation_history = []
            conversation_history.append({
                    "role": "user",
                    "content": question
                })
            conversation_history.append({
                    "role": "assistant",
                    "content": completion.choices[0].message.content
                })
            self.conversation_manager.update_history(conversation_id, conversation_history)
        return conversation_history
