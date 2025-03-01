class ProcessingError(Exception):
    """Base exception for processing errors"""
    pass

class ExtractionError(ProcessingError):
    """Raised when text extraction fails"""
    pass

class ChunkingError(ProcessingError):
    """Raised when text chunking fails"""
    pass

class EmbeddingError(ProcessingError):
    """Raised when embedding generation fails"""
    pass

class StorageError(ProcessingError):
    """Raised when storage operations fail"""
    pass
