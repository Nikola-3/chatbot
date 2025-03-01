# TODO: Fix failing tests due to incompatibility between pyfakefs and async tests with pathlib.Path
import pytest
import pathlib
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
# from pyfakefs.fake_filesystem import FakeFilesystem
from pyfakefs.fake_filesystem_unittest import patchfs
from backend.storage.file_system_storage import FileSystemStorage
from backend.storage.storage_interface import DocumentMetadata

# @pytest.fixture
# def fake_filesystem():
#     fs = FakeFilesystem()
#     # Set up fake filesystem
#     fs.create_dir("/fakepath")
#     return fs


@pytest.mark.asyncio
@patchfs(modules_to_reload=[pathlib.Path])
@patch("backend.storage.file_system_storage.open")
async def test_save_document(fs):
    # Set up fake filesystem
    fs.create_dir("/fakepath/documents")
    mock_exists = fs.exists
    mock_is_dir = fs.isdir
    mock_mkdir = fs.mkdir
    mock_aiofiles = fs.open

    # Given
    mock_exists.return_value = False
    mock_is_dir.return_value = True
    content = b"Test content"
    doc_id = uuid4()
    metadata = DocumentMetadata(id=doc_id, filename="test.pdf", mime_type="application/pdf", size_bytes=len(content))

    storage = FileSystemStorage(base_path="/fakepath/documents")
    
    assert mock_mkdir.call_count == 2  # mkdir should be called once for metadata once for docs

    mock_aiofiles.return_value = AsyncMock()

    # When
    result = await storage.save_document(content, metadata)

    # Then
    assert result == doc_id

    fake_doc_path = f"/fakepath/documents/{doc_id}"
    assert fake_filesystem.exists(fake_doc_path)  # Ensure that the folder is created
    assert fake_filesystem.exists(f"{fake_doc_path}/original")  # Check if the original file was created
    assert fake_filesystem.exists(f"{fake_doc_path}/metadata.json")  # Check if the metadata file was created

    mock_aiofiles.assert_any_call(f"{fake_doc_path}/original", "wb")
    mock_aiofiles.assert_any_call(f"{fake_doc_path}/metadata.json", "w")


@pytest.mark.asyncio
@patch("backend.storage.file_system_storage.aiofiles.open")
@patch("backend.storage.file_system_storage.Path.exists")
@patch("backend.storage.file_system_storage.Path.is_dir")
async def test_save_document_directory_exists(mock_is_dir, mock_exists, mock_aiofiles):
    # Given
    mock_exists.return_value = True
    mock_is_dir.return_value = True
    content = b"Test content"
    doc_id = uuid4()
    metadata = DocumentMetadata(id=doc_id, filename="test.pdf", mime_type="application/pdf", size_bytes=len(content))
    storage = FileSystemStorage(base_path="test_path")

    mock_aiofiles.return_value = AsyncMock()

    # When
    result = await storage.save_document(content, metadata)

    # Then
    assert result == doc_id
    mock_aiofiles.assert_any_call(storage.docs_path / str(doc_id) / "original", "wb")
    mock_aiofiles.assert_any_call(storage.docs_path / str(doc_id) / "metadata.json", "w")


@pytest.mark.asyncio
@patch("backend.storage.file_system_storage.shutil.rmtree")
@patch("backend.storage.file_system_storage.Path.exists")
@patch("backend.storage.file_system_storage.Path.is_dir")
async def test_delete_document(mock_is_dir, mock_exists, mock_rmtree):
    # Given
    doc_id = uuid4()
    storage = FileSystemStorage(base_path="test_path")
    doc_path = storage.docs_path / str(doc_id)

    mock_exists.return_value = True
    mock_is_dir.return_value = True
    mock_rmtree.return_value = None

    # When
    result = await storage.delete_document(doc_id)

    # Then
    assert result is True
    mock_rmtree.assert_called_once_with(doc_path)


@pytest.mark.asyncio
@patch("backend.storage.file_system_storage.shutil.rmtree")
@patch("backend.storage.file_system_storage.Path.exists")
@patch("backend.storage.file_system_storage.Path.is_dir")
async def test_delete_document_directory_not_found(mock_is_dir, mock_exists, mock_rmtree):
    # Given
    doc_id = uuid4()
    storage = FileSystemStorage(base_path="test_path")
    doc_path = storage.docs_path / str(doc_id)

    mock_exists.return_value = False
    mock_is_dir.return_value = False
    mock_rmtree.return_value = None

    # When
    result = await storage.delete_document(doc_id)

    # Then
    assert result is False
    mock_rmtree.assert_not_called()


@pytest.mark.asyncio
@patch("backend.storage.file_system_storage.shutil.rmtree")
@patch("backend.storage.file_system_storage.Path.exists")
@patch("backend.storage.file_system_storage.Path.is_dir")
async def test_delete_document_error_handling(mock_is_dir, mock_exists, mock_rmtree):
    # Given
    doc_id = uuid4()
    storage = FileSystemStorage(base_path="test_path")
    doc_path = storage.docs_path / str(doc_id)

    mock_exists.return_value = True
    mock_is_dir.return_value = True
    mock_rmtree.side_effect = Exception("Test Exception")

    # When / Then: Ensure the exception is raised and properly propagated
    with pytest.raises(Exception):
        await storage.delete_document(doc_id)
    mock_rmtree.assert_called_once_with(doc_path)

