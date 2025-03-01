import pytest
from datetime import datetime
from processing.progress import ProcessingProgress
import time

@pytest.fixture
def progress():
    return ProcessingProgress(doc_id="test-doc-123")

def test_progress_initialization(progress):
    assert progress.doc_id == "test-doc-123"
    assert progress.total_chunks == 0
    assert progress.processed_chunks == 0
    assert progress.start_time is None
    assert progress.end_time is None
    assert progress.current_stage is None
    assert progress.error is None

def test_start_processing(progress):
    # When
    progress.start(total_chunks=10)
    
    # Then
    assert progress.total_chunks == 10
    assert isinstance(progress.start_time, datetime)
    assert progress.end_time is None

def test_update_progress(progress):
    # Given
    progress.start(total_chunks=10)
    
    # When
    progress.update(processed_chunks=5, stage="chunking")
    
    # Then
    assert progress.processed_chunks == 5
    assert progress.current_stage == "chunking"
    assert progress.progress_percentage == 50.0

def test_complete_processing(progress):
    # Given
    progress.start(total_chunks=10)
    progress.update(processed_chunks=10, stage="completed")
    
    # When
    progress.complete()
    
    # Then
    assert isinstance(progress.end_time, datetime)
    assert progress.progress_percentage == 100.0

def test_fail_processing(progress):
    # Given
    progress.start(total_chunks=10)
    progress.update(processed_chunks=5, stage="chunking")
    
    # When
    progress.fail("Test error occurred")
    
    # Then
    assert progress.error == "Test error occurred"
    assert isinstance(progress.end_time, datetime)
    assert progress.progress_percentage == 50.0

def test_progress_percentage_zero_chunks(progress):
    assert progress.progress_percentage == 0

def test_to_dict_representation(progress):
    # Given
    progress.start(total_chunks=10)
    progress.update(processed_chunks=5, stage="processing")
    
    # When
    result = progress.to_dict()
    
    # Then
    assert isinstance(result, dict)
    assert result["doc_id"] == "test-doc-123"
    assert result["progress"] == 50.0
    assert result["stage"] == "processing"
    assert result["error"] is None
    assert isinstance(result["start_time"], str)
    assert result["end_time"] is None

def test_to_dict_with_error(progress):
    # Given
    progress.start(total_chunks=10)
    progress.fail("Test error")
    
    # When
    result = progress.to_dict()
    
    # Then
    assert result["error"] == "Test error"
    assert isinstance(result["end_time"], str)
