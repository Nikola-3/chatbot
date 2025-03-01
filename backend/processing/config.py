from pydantic import BaseModel, Field

class ProcessingConfig(BaseModel):
    chunk_size: int = Field(default=512, gt=0)
    chunk_overlap: int = Field(default=50, ge=0)
    embedding_model: str = Field(default="text-embedding-ada-002")
    min_chunk_size: int = Field(default=100, gt=0)
    max_retries: int = Field(default=3, gt=0)
