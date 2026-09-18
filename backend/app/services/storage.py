"""Object storage abstraction.

Dev: writes to local disk under LOCAL_STORAGE_DIR.
Prod: swap for S3-compatible storage (boto3) behind the same interface.
Only metadata + storage keys live in the DB (section 15).
"""
import os
import uuid
from pathlib import Path

from app.core.config import settings


class StorageService:
    def __init__(self) -> None:
        self.use_s3 = bool(settings.S3_ENDPOINT_URL and settings.S3_ACCESS_KEY)
        if self.use_s3:
            import boto3

            self._s3 = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
            )
        else:
            self.root = Path(settings.LOCAL_STORAGE_DIR)
            self.root.mkdir(parents=True, exist_ok=True)

    def build_key(self, prefix: str, filename: str) -> str:
        ext = os.path.splitext(filename)[1] or ".bin"
        return f"{prefix}/{uuid.uuid4().hex}{ext}"

    def save_bytes(self, key: str, data: bytes) -> str:
        if self.use_s3:
            self._s3.put_object(Bucket=settings.S3_BUCKET, Key=key, Body=data)
        else:
            path = self.root / key
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        return key

    def public_url(self, key: str) -> str:
        if self.use_s3:
            return f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET}/{key}"
        return f"/media/{key}"

    def read_bytes(self, key: str) -> bytes:
        if self.use_s3:
            obj = self._s3.get_object(Bucket=settings.S3_BUCKET, Key=key)
            return obj["Body"].read()
        return (self.root / key).read_bytes()

    def data_uri(self, key: str) -> str:
        """Base64 data URI — lets external AI APIs read a locally-stored image
        without a public URL."""
        import base64

        ext = os.path.splitext(key)[1].lstrip(".").lower() or "png"
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, "png")
        b64 = base64.b64encode(self.read_bytes(key)).decode("ascii")
        return f"data:image/{mime};base64,{b64}"


storage = StorageService()
