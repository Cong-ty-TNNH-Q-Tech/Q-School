import aioboto3
from botocore.exceptions import ClientError
from app.application.ports.outbound.storage_service import IStorageService
from app.core.config import settings

class R2StorageAdapter(IStorageService):
    """
    Adapter cho Cloudflare R2 / MinIO sử dụng aioboto3.
    """
    def __init__(self):
        self.session = aioboto3.Session()
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.bucket_name = settings.S3_BUCKET_NAME
        self.public_url = settings.S3_PUBLIC_URL.rstrip('/')
        
    def _get_client(self):
        return self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='auto'  # Cloudflare R2 requires region to be auto or empty, MinIO ignores it
        )
        
    def _extract_key_from_url(self, file_url: str) -> str:
        if file_url.startswith(self.public_url):
            return file_url[len(self.public_url) + 1:]
        # Fallback if it's just a filename or different format
        return file_url.split('/')[-1]

    async def upload(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        *,
        is_public: bool = False,
    ) -> str:
        """
        Upload file và trả về URL để lưu vào DB.
        """
        extra_args = {'ContentType': content_type}
        # R2 doesn't heavily rely on ACLs like S3, but we can set it if it's public.
        # However, to be safe with R2/MinIO, it's better to manage public access via bucket policies.
        # But we'll add ACL='public-read' just in case if the bucket allows it.
        # Actually, let's omit ACL unless explicitly needed, since R2 might reject ACLs if not configured.
        
        async with self._get_client() as s3_client:
            await s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=file_bytes,
                **extra_args
            )
            
        return f"{self.public_url}/{filename}"

    async def delete(self, file_url: str) -> None:
        """Xóa file khỏi storage theo URL."""
        key = self._extract_key_from_url(file_url)
        async with self._get_client() as s3_client:
            await s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )

    async def get_presigned_url(self, file_url: str, expires_in: int = 3600) -> str:
        """
        Tạo presigned URL tạm thời cho private files.
        """
        key = self._extract_key_from_url(file_url)
        async with self._get_client() as s3_client:
            url = await s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expires_in
            )
            return url
