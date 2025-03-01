from fastapi import APIRouter, UploadFile, HTTPException
from models import ProcessingStatus
from processing.exceptions import ProcessingError
from dependencies import storage_manager, document_processor

router = APIRouter()

@router.post("/upload", response_model=ProcessingStatus)
async def upload_document(file: UploadFile):
    try:
        content = await file.read()  # Get file content as bytes
        
        # Process the document
        doc_id = await document_processor.process_document(
            content=content,
            filename=file.filename
        )
        
        # Update status 
        return ProcessingStatus(
            status="completed",
            message=f"Document {doc_id} processed successfully"
        )
        
    except ProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during processing: {str(e)}"
        )

@router.get("/{doc_id}/status", response_model=ProcessingStatus)
async def get_document_status(doc_id: str):
    try:
        # Get document status from storage manager
        doc = await storage_manager.get_document_metadata(doc_id)
        status = "ready" if doc else "not_found"
        return ProcessingStatus(status=status)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Document not found")

