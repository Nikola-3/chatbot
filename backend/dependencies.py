from openai import AsyncOpenAI
from storage.storage_manager import StorageManager
from storage.file_system_storage import FileSystemStorage
from storage.vector_storage import VectorStorage
from storage.metadata_store import MetadataStore
from config import get_settings
from processing.config import ProcessingConfig
from processing.prompt_manager import PromptManager
from processing.query_processor import QueryProcessor
from processing.completion_handler import CompletionHandler
from processing.processor import DocumentProcessor

settings = get_settings()

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

# Initialize storage components
file_storage = FileSystemStorage(settings.upload_folder)
vector_storage = VectorStorage(settings.chroma_db_path)
metadata_storage = MetadataStore(settings.postgres_url)

# Initialize storage manager
storage_manager = StorageManager(
    file_storage=file_storage,
    vector_storage=vector_storage,
    metadata_storage=metadata_storage
)

# Initialize processing components
processing_config = ProcessingConfig()
prompt_manager = PromptManager()

# Initialize document processor
document_processor = DocumentProcessor(
    storage=storage_manager,
    openai_client=openai_client,
    config=processing_config
)

query_processor = QueryProcessor(
    storage=storage_manager,
    openai_client=openai_client,
    config=processing_config
)
completion_handler = CompletionHandler(
    query_processor=query_processor,
    prompt_manager=prompt_manager,
    openai_client=openai_client
)

async def init_dependencies():
    """Initialize async components"""
    await metadata_storage.initialize()