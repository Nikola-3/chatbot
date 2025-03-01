from typing import Optional

class PromptManager:
    DEFAULT_TEMPLATE = """Use the following context to answer the question.
If the answer cannot be found in the context, respond with "I don't have enough information to answer that."
Always maintain a natural conversational style and refer to previous context when relevant.

Context:
{context}

Question: {question}

Answer:"""

    def __init__(self, template: Optional[str] = None):
        self.template = template or self.DEFAULT_TEMPLATE

    def create_prompt(self, question: str, context: str) -> str:
        """Create a prompt by combining the question and context"""
        return self.template.format(
            context=context,
            question=question
        )

    def create_chat_messages(
        self,
        question: str,
        context: str,
        history: Optional[list[dict[str, str]]] = None
    ) -> list[dict[str, str]]:
        """Create chat messages with conversation history"""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Answer questions based only on the provided context. Maintain conversation continuity."
            }
        ]

        
        if history:
            messages.extend(history)

        # Add current question with context
        messages.append({
            "role": "user",
            "content": self.create_prompt(question, context)
        })

        return messages
