from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api import chat, documents
import uvicorn
from dependencies import init_dependencies

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    await init_dependencies()
    yield
    # Shutdown

app = FastAPI(
    title="RAG Chatbot",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers with explicit prefixes
app.include_router(
    chat.router,
    prefix="",
    tags=["chat"]
)
app.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001)
