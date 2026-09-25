"""
S3 Service
----------
Handles receipt image/PDF uploads to Amazon S3.

If S3 is not reachable (no AWS account configured locally), receipts
are stored on the local filesystem under /uploads instead, and a local
URL is returned. This keeps the app fully functional for local demos.
"""

import os
import logging
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from werkzeug.utils import secure_filename

from config.config import get_config
from utils.helpers import generate_id

logger = logging.getLogger(__name__)
config = get_config()


class S3Service:
    def __init__(self):
        self.use_aws = False
        self.client = None
        self._try_connect()
        os.makedirs(config.LOCAL_UPLOAD_FOLDER, exist_ok=True)

    def _try_connect(self):
        try:
            self.client = boto3.client("s3", region_name=config.AWS_REGION)
            # Verify bucket is reachable
            self.client.head_bucket(Bucket=config.S3_BUCKET_NAME)
            self.use_aws = True
            logger.info("Connected to S3 bucket '%s'.", config.S3_BUCKET_NAME)
        except Exception as exc:
            if not config.USE_LOCAL_STORAGE_FALLBACK:
                logger.error("S3 is unavailable and local fallback is disabled: %s", exc)
                raise RuntimeError("S3 is unavailable. Check the IAM role, bucket, and AWS region.") from exc
            logger.warning(
                "S3 not reachable (%s). Falling back to local filesystem "
                "storage for local development.", exc,
            )
            self.use_aws = False

    def upload_receipt(self, file_storage, user_id: str) -> dict:
        """
        Uploads a receipt file. Returns dict with 'key' and 'url'.
        `file_storage` is a Werkzeug FileStorage object from Flask's request.files.
        """
        original_name = secure_filename(file_storage.filename)
        extension = original_name.rsplit(".", 1)[1].lower() if "." in original_name else "bin"
        unique_name = f"{user_id}/{generate_id('receipt_')}.{extension}"

        if self.use_aws:
            try:
                self.client.upload_fileobj(
                    file_storage,
                    config.S3_BUCKET_NAME,
                    unique_name,
                    ExtraArgs={"ContentType": file_storage.mimetype},
                )
                url = self.get_receipt_url(unique_name)
                return {"key": unique_name, "url": url}
            except (BotoCoreError, ClientError) as exc:
                logger.error("S3 upload failed: %s", exc)
                raise RuntimeError("Failed to upload receipt to cloud storage.")
        else:
            # Local fallback
            safe_dir = os.path.join(config.LOCAL_UPLOAD_FOLDER, user_id)
            os.makedirs(safe_dir, exist_ok=True)
            local_filename = f"{generate_id('receipt_')}.{extension}"
            local_path = os.path.join(safe_dir, local_filename)
            file_storage.save(local_path)
            key = f"{user_id}/{local_filename}"
            return {"key": key, "url": f"/uploads/{key}"}

    def get_receipt_url(self, key: str) -> str:
        """Returns a presigned URL (AWS) or local static path (fallback)."""
        if self.use_aws:
            try:
                return self.client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": config.S3_BUCKET_NAME, "Key": key},
                    ExpiresIn=config.S3_PRESIGNED_URL_EXPIRY,
                )
            except (BotoCoreError, ClientError) as exc:
                logger.error("Failed to generate presigned URL: %s", exc)
                return ""
        return f"/uploads/{key}"

    def delete_receipt(self, key: str) -> bool:
        if not key:
            return False
        if self.use_aws:
            try:
                self.client.delete_object(Bucket=config.S3_BUCKET_NAME, Key=key)
                return True
            except (BotoCoreError, ClientError) as exc:
                logger.error("Failed to delete S3 object: %s", exc)
                return False
        else:
            local_path = os.path.join(config.LOCAL_UPLOAD_FOLDER, key)
            if os.path.exists(local_path):
                os.remove(local_path)
                return True
            return False


s3_service = S3Service()
