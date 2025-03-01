from fastapi import APIRouter, HTTPException
from typing import Optional
from models import ChatMessage, ChatResponse
from processing.exceptions import ProcessingError
from dependencies import completion_handler

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    conversation_id: Optional[str] = None
):
    try:
        response = await completion_handler.get_response(
            question=message.content,
            conversation_id=conversation_id
        )
        
        return ChatResponse(
            response=response["answer"],
            sources=[chunk.document_id for chunk in response["chunks"]]
        )
            
    except ProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during chat processing: {str(e)}"
        )
