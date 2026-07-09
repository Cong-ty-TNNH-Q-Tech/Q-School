import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.adapters.storage.r2_adapter import R2StorageAdapter
from botocore.exceptions import ClientError

@pytest.fixture
def mock_aioboto3_session():
    with patch("app.adapters.storage.r2_adapter.aioboto3.Session") as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # S3 client mock
        mock_s3_client = AsyncMock()
        
        # Setup context manager for client
        mock_client_cm = AsyncMock()
        mock_client_cm.__aenter__.return_value = mock_s3_client
        mock_client_cm.__aexit__.return_value = None
        
        mock_session.client.return_value = mock_client_cm
        
        yield mock_session, mock_s3_client

@pytest.mark.asyncio
async def test_r2_adapter_upload_public(mock_aioboto3_session):
    _, mock_s3_client = mock_aioboto3_session
    adapter = R2StorageAdapter()
    
    url = await adapter.upload(b"test data", "test.txt", "text/plain", is_public=True)
    
    # Verify s3 call
    mock_s3_client.put_object.assert_called_once_with(
        Bucket=adapter.bucket_name,
        Key="test.txt",
        Body=b"test data",
        ContentType="text/plain"
    )
    assert url == f"{adapter.public_url}/test.txt"

@pytest.mark.asyncio
async def test_r2_adapter_upload_private(mock_aioboto3_session):
    _, mock_s3_client = mock_aioboto3_session
    adapter = R2StorageAdapter()
    
    url = await adapter.upload(b"test data", "test.txt", "text/plain", is_public=False)
    
    assert url == f"s3://{adapter.bucket_name}/test.txt"

@pytest.mark.asyncio
async def test_r2_adapter_delete(mock_aioboto3_session):
    _, mock_s3_client = mock_aioboto3_session
    adapter = R2StorageAdapter()
    
    # Adapter sẽ trích xuất key "test.txt" từ URL
    await adapter.delete(f"s3://{adapter.bucket_name}/test.txt")
    
    mock_s3_client.delete_object.assert_called_once_with(
        Bucket=adapter.bucket_name,
        Key="test.txt"
    )

@pytest.mark.asyncio
async def test_r2_adapter_get_presigned_url(mock_aioboto3_session):
    _, mock_s3_client = mock_aioboto3_session
    mock_s3_client.generate_presigned_url.return_value = "http://presigned"
    adapter = R2StorageAdapter()
    
    url = await adapter.get_presigned_url(f"s3://{adapter.bucket_name}/test.txt", 3600)
    
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        ClientMethod='get_object',
        Params={'Bucket': adapter.bucket_name, 'Key': "test.txt"},
        ExpiresIn=3600
    )
    assert url == "http://presigned"

@pytest.mark.asyncio
async def test_r2_adapter_get_presigned_url_public():
    # Nếu file đã là public, trả về nguyên mẫu
    adapter = R2StorageAdapter()
    public_url = f"{adapter.public_url}/test.txt"
    
    url = await adapter.get_presigned_url(public_url, 3600)
    
    assert url == public_url

def test_r2_adapter_extract_key_from_url():
    adapter = R2StorageAdapter()
    adapter.public_url = "http://localhost:9000/bucket"
    adapter.bucket_name = "test-bucket"
    
    # Public url
    key1 = adapter._extract_key_from_url("http://localhost:9000/bucket/folder/file.png")
    assert key1 == "folder/file.png"
    
    # S3 schema
    key2 = adapter._extract_key_from_url("s3://test-bucket/folder/file.png")
    assert key2 == "folder/file.png"
    
    # Raw key
    key3 = adapter._extract_key_from_url("folder/file.png")
    assert key3 == "folder/file.png"

@pytest.mark.asyncio
async def test_r2_adapter_upload_exception(mock_aioboto3_session):
    _, mock_s3_client = mock_aioboto3_session
    mock_s3_client.put_object.side_effect = ClientError({"Error": {"Code": "500", "Message": "Error"}}, "put_object")
    adapter = R2StorageAdapter()
    
    with pytest.raises(Exception, match="Storage upload error"):
        await adapter.upload(b"data", "test.txt", "text/plain")

@pytest.mark.asyncio
async def test_r2_adapter_download(mock_aioboto3_session):
    _, mock_s3_client = mock_aioboto3_session
    mock_response = {'Body': AsyncMock()}
    mock_response['Body'].read.return_value = b"downloaded data"
    mock_s3_client.get_object.return_value = mock_response
    adapter = R2StorageAdapter()
    
    data = await adapter.download(f"s3://{adapter.bucket_name}/test.txt")
    
    mock_s3_client.get_object.assert_called_once_with(
        Bucket=adapter.bucket_name,
        Key="test.txt"
    )
    assert data == b"downloaded data"

@pytest.mark.asyncio
async def test_r2_adapter_download_exception(mock_aioboto3_session):
    _, mock_s3_client = mock_aioboto3_session
    mock_s3_client.get_object.side_effect = ClientError({"Error": {"Code": "404", "Message": "Not Found"}}, "get_object")
    adapter = R2StorageAdapter()
    
    with pytest.raises(Exception, match="Storage download error"):
        await adapter.download(f"s3://{adapter.bucket_name}/test.txt")
