from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone

@dataclass
class ProcessingProgress:
    doc_id: str
    total_chunks: int = 0
    processed_chunks: int = 0
    start_time: datetime = None
    end_time: datetime = None
    current_stage: str = None
    error: Optional[str] = None

    def start(self, total_chunks: int):
        self.total_chunks = total_chunks
        self.start_time = datetime.now()

    def update(self, processed_chunks: int, stage: str):
        self.processed_chunks = processed_chunks
        self.current_stage = stage

    def complete(self):
        self.end_time = datetime.now()

    def fail(self, error: str):
        self.error = error
        self.end_time = datetime.now()

    @property
    def progress_percentage(self) -> float:
        if self.total_chunks == 0:
            return 0
        return (self.processed_chunks / self.total_chunks) * 100

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "progress": self.progress_percentage,
            "stage": self.current_stage,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }
