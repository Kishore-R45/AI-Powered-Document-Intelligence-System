"""
AWS S3 service for file storage operations.
"""

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config as BotoConfig
import uuid
from config import Config


class S3Service:
    """AWS S3 service for file storage and retrieval."""
    
    _client = None
    
    @classmethod
    def get_client(cls):
        """Get or create S3 client."""
        if cls._client is None:
            cls._client = boto3.client(
                's3',
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                region_name=Config.AWS_S3_REGION,
                config=BotoConfig(signature_version='s3v4')
            )
        return cls._client
    
    @staticmethod
    def generate_s3_key(user_id: str, document_id: str, filename: str) -> str:
        """
        Generate a unique S3 key for a document.
        
        Args:
            user_id: User's ID
            document_id: Document ID
            filename: Original filename
            
        Returns:
            S3 key path
        """
        # Sanitize filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in '._-')
        return f"{user_id}/{document_id}/{safe_filename}"
    
    @classmethod
    def upload_file(cls, file_obj, s3_key: str, content_type: str = None) -> bool:
        """
        Upload a file to S3.
        
        Args:
            file_obj: File object to upload
            s3_key: S3 key for the file
            content_type: MIME type of the file
            
        Returns:
            True if upload successful
        """
        try:
            client = cls.get_client()
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            client.upload_fileobj(
                file_obj,
                Config.AWS_S3_BUCKET_NAME,
                s3_key,
                ExtraArgs=extra_args
            )
            return True
        except ClientError as e:
            print(f"S3 upload error: {e}")
            return False
    
    @classmethod
    def upload_bytes(cls, data: bytes, s3_key: str, content_type: str = None) -> bool:
        """
        Upload bytes data to S3.
        
        Args:
            data: Bytes to upload
            s3_key: S3 key for the file
            content_type: MIME type of the file
            
        Returns:
            True if upload successful
        """
        from io import BytesIO
        return cls.upload_file(BytesIO(data), s3_key, content_type)
    
    @classmethod
    def download_file(cls, s3_key: str) -> bytes | None:
        """
        Download a file from S3.
        
        Args:
            s3_key: S3 key of the file
            
        Returns:
            File contents as bytes, or None if failed
        """
        try:
            from io import BytesIO
            client = cls.get_client()
            buffer = BytesIO()
            client.download_fileobj(Config.AWS_S3_BUCKET_NAME, s3_key, buffer)
            buffer.seek(0)
            return buffer.read()
        except ClientError as e:
            print(f"S3 download error: {e}")
            return None
    
    @classmethod
    def get_presigned_url(cls, s3_key: str, expiration: int = None, for_download: bool = False) -> str | None:
        """
        Generate a presigned URL for accessing a file.
        
        Args:
            s3_key: S3 key of the file
            expiration: URL expiration in seconds (default from config)
            for_download: If True, force download; if False, open in browser
            
        Returns:
            Presigned URL or None if failed
        """
        try:
            client = cls.get_client()
            expiration = expiration or Config.S3_PRESIGNED_URL_EXPIRY
            
            params = {
                'Bucket': Config.AWS_S3_BUCKET_NAME,
                'Key': s3_key,
            }
            
            if for_download:
                params['ResponseContentDisposition'] = 'attachment'
            else:
                params['ResponseContentDisposition'] = 'inline'
            
            url = client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"S3 presigned URL error: {e}")
            return None
    
    @classmethod
    def delete_file(cls, s3_key: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            s3_key: S3 key of the file
            
        Returns:
            True if deletion successful
        """
        try:
            client = cls.get_client()
            client.delete_object(
                Bucket=Config.AWS_S3_BUCKET_NAME,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"S3 delete error: {e}")
            return False
    
    @classmethod
    def delete_folder(cls, prefix: str) -> bool:
        """
        Delete all files with a given prefix (folder).
        
        Args:
            prefix: S3 key prefix to delete
            
        Returns:
            True if deletion successful
        """
        try:
            client = cls.get_client()
            
            # List all objects with the prefix
            paginator = client.get_paginator('list_objects_v2')
            pages = paginator.paginate(
                Bucket=Config.AWS_S3_BUCKET_NAME,
                Prefix=prefix
            )
            
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                objects = [{'Key': obj['Key']} for obj in page['Contents']]
                client.delete_objects(
                    Bucket=Config.AWS_S3_BUCKET_NAME,
                    Delete={'Objects': objects}
                )
            
            return True
        except ClientError as e:
            print(f"S3 folder delete error: {e}")
            return False
    
    @classmethod
    def file_exists(cls, s3_key: str) -> bool:
        """
        Check if a file exists in S3.
        
        Args:
            s3_key: S3 key to check
            
        Returns:
            True if file exists
        """
        try:
            client = cls.get_client()
            client.head_object(Bucket=Config.AWS_S3_BUCKET_NAME, Key=s3_key)
            return True
        except ClientError:
            return False
