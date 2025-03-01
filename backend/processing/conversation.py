from typing import Optional
from datetime import datetime, timedelta, timezone
import threading
import time

class ConversationManager:
    def __init__(
        self,
        max_history: int = 20,
        expiry_minutes: int = 60,
        cleanup_interval: int = 60
    ):
        self.max_history = max_history
        self.expiry_minutes = expiry_minutes
        self.conversations: dict[str, dict] = {}
        self.last_accessed: dict[str, datetime] = {}
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            args=(cleanup_interval,),
            daemon=True
        )
        self.cleanup_thread.start()

    def get_history(self, conversation_id: str) -> Optional[list[dict[str, str]]]:
        """Get conversation history if it exists and update last accessed time"""
        if conversation_id in self.conversations:
            self.last_accessed[conversation_id] = datetime.now()
            return self.conversations[conversation_id]
        return None

    def update_history(self, conversation_id: str, messages: list[dict[str, str]]):
        """Update conversation history, maintaining size limit"""
        # Keep only the most recent messages within the limit
        if len(messages) > self.max_history:
            messages = messages[-self.max_history:]
        
        self.conversations[conversation_id] = messages
        self.last_accessed[conversation_id] = datetime.now()

    def _cleanup_loop(self, interval: int):
        """Periodically clean up expired conversations"""
        while True:
            self._cleanup_expired()
            time.sleep(interval)

    def _cleanup_expired(self):
        """Remove conversations that have expired"""
        now = datetime.now()
        expiry = timedelta(minutes=self.expiry_minutes)
        
        expired = [
            conv_id for conv_id, last_access in self.last_accessed.items()
            if now - last_access > expiry
        ]
        
        for conv_id in expired:
            self.conversations.pop(conv_id, None)
            self.last_accessed.pop(conv_id, None)
