from aiofiles import open
# TODO: revise use of shutil in case it is used to save or update files,
# as it does not work consistently between MacOS and other systems
import shutil
from uuid import UUID
from pathlib import Path
from .storage_interface import StorageInterface, DocumentMetadata

class FileSystemStorage(StorageInterface):
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.docs_path = self.base_path / "documents"
        self.temp_path = self.base_path / "temp"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        self.docs_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
    
    async def save_document(self, content: bytes, metadata: DocumentMetadata) -> UUID:
        doc_path = self.docs_path / str(metadata.id)
        doc_path.mkdir(exist_ok=True)
        
        async with open(doc_path / "original", "wb") as f:
            await f.write(content)
            
        async with open(doc_path / "metadata.json", "w") as f:
            await f.write(metadata.model_dump_json())
            
        return metadata.id
    
    async def delete_document(self, doc_id: UUID) -> bool:
        doc_path = self.docs_path / str(doc_id)
        try:
            if doc_path.exists() and doc_path.is_dir():
                shutil.rmtree(doc_path)
                return True
        except Exception as e:
            # TODO: Handle error properly 
            raise e
        return False
