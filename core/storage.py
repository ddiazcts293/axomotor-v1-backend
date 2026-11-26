from typing import Optional
from pathlib import Path
import uuid

import boto3
from botocore.client import Config
from fastapi import HTTPException, UploadFile, status

from core.config import settings

class S3File():
    def __init__(self, key: str, content_type: str, size_bytes: int):
        self.key: str = key
        self.content_type: str = content_type
        self.size_bytes: int = size_bytes

s3_internal_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_INTERNAL_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)

s3_public_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_PUBLIC_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)

async def validate_and_upload_file(
    file: UploadFile,
    directory: str = "incidents"
) -> S3File:
    # 1. Validar MIME type declarado
    if file.content_type not in settings.ALLOWED_FILE_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file format. Allowed formats: {', '.join(settings.ALLOWED_FILE_FORMATS.keys())}",
        )

    # 2. Validar extensión real del nombre de archivo
    ext_original = Path(file.filename or "").suffix.lower()
    ext_expected = settings.ALLOWED_FILE_FORMATS[file.content_type]
    if ext_original != ext_expected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension",
        )

    # 3. Leer y validar tamaño máximo sin desbordar memoria
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File empty")
    if len(content) > (settings.MAXIMUM_FILE_SIZE_MB * 1024 * 1024):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. The maximum file size is {settings.MAXIMUM_FILE_SIZE_MB} MB",
        )

    # 4. Generar nombre único (UUID) para evitar colisiones y Path Traversal
    object_key = f"{directory}/{uuid.uuid4().hex}{ext_expected}"

    s3_internal_client.put_object(
        Bucket=settings.S3_BUCKET,
        Key=object_key,
        Body=content,
        ContentType=file.content_type,
    )

    return S3File(
        key = object_key,
        content_type = file.content_type,
        size_bytes = len(content),
    )

def generate_download_url(
    object_key: str,
    expiration_minutes: Optional[int] = None
) -> str:
    if expiration_minutes is None:
        expiration_minutes = settings.DOWNLOAD_URL_EXPIRE_MINUTES

    return s3_public_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": settings.S3_BUCKET,
            "Key": object_key,
        },
        ExpiresIn=expiration_minutes * 60,
    )

def delete_file(object_key: str) -> None:
    s3_internal_client.delete_object(
        Bucket=settings.S3_BUCKET,
        Key=object_key,
    )
