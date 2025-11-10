import os
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Optional, BinaryIO, Tuple

from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from azure.core.exceptions import (
    ResourceNotFoundError,
    ClientAuthenticationError,
    HttpResponseError,
)
from fastapi import UploadFile

from loguru import logger


class AzureBlobService:
    """Minimal Azure Blob helper with SAS URL generation.

    All configuration can be passed explicitly via constructor. If omitted, falls back
    to environment variables. By default, it does not warn at startup when not
    configured; operations will error if required values are missing.
    """

    def __init__(
        self,
        *,
        connection_string: Optional[str] = None,
        account_key: Optional[str] = None,
        container_name: Optional[str] = None,
        base_blob_url: Optional[str] = None,
        sas_token: Optional[str] = None,
        warn_if_unconfigured: bool = False,
    ) -> None:
        self.container_name = container_name or os.getenv("AZURE_BLOB_CONTAINER", "uploads")
        self.connection_string = connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.account_key = account_key or os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        self.sas_token = sas_token or os.getenv("AZURE_SAS_TOKEN")
        self.base_blob_url = base_blob_url or os.getenv("AZURE_BLOB_URL")

        if warn_if_unconfigured and not self.connection_string:
            logger.warning(
                "Azure Storage connection string not configured; blob operations may fail."
            )

    def _get_blob_service(self) -> BlobServiceClient:
        if not self.connection_string:
            raise RuntimeError("AZURE_STORAGE_CONNECTION_STRING not configured")
        clean = self.connection_string.strip().strip('"').strip("'")
        return BlobServiceClient.from_connection_string(clean)

    def _parse_account_from_connection_string(self) -> Tuple[Optional[str], Optional[str]]:
        if not self.connection_string:
            return None, None
        try:
            clean = self.connection_string.strip().strip('"').strip("'")
            parts = dict(seg.split("=", 1) for seg in clean.split(";") if "=" in seg)
            account_name = parts.get("AccountName")
            account_key = parts.get("AccountKey") or self.account_key
            return account_name, account_key
        except Exception:
            return None, None

    def _ensure_container(self, client: BlobServiceClient) -> None:
        try:
            client.create_container(self.container_name)
        except Exception:
            pass

    def _generate_sas_url(self, blob_name: str, expiry_days: int = 730) -> str:
        account_name, account_key = self._parse_account_from_connection_string()
        if not account_name:
            try:
                client = self._get_blob_service()
                account_name = getattr(client, "account_name", None)
            except Exception:
                account_name = None

        account_key = account_key or self.account_key
        if not account_name or not account_key:
            raise RuntimeError("Azure Storage account name/key not configured; cannot generate SAS")

        start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        expiry_time = start_time + timedelta(days=expiry_days)
        sas = generate_blob_sas(
            account_name=account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            start=start_time,
            expiry=expiry_time,
            protocol="https",
        )

        if self.base_blob_url:
            base_url = self.base_blob_url.strip().strip('"').strip("'").rstrip("/")
            return f"{base_url}/{blob_name}?{sas}"
        return (
            f"https://{account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas}"
        )

    async def upload_file(self, file: UploadFile, blob_path: str) -> Optional[str]:
        """Upload a file to Azure Blob Storage and return a SAS URL.

        Args:
            file: File to upload
            blob_path: Destination path in the container

        Returns:
            SAS URL if successful, None on error
        """
        if not self.connection_string:
            logger.error("Azure Storage connection string not configured")
            return None
        try:
            client = self._get_blob_service()
            self._ensure_container(client)
            container = client.get_container_client(self.container_name)
            content = await file.read()
            blob_client = container.get_blob_client(blob_path)
            blob_client.upload_blob(
                content,
                overwrite=True,
                content_type=file.content_type or "application/octet-stream",
            )
            return self._generate_sas_url(blob_path)
        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed uploading {file.filename}: {e}")
            return None
        except HttpResponseError as e:
            logger.error(
                f"Azure service error uploading {file.filename}: {e.status_code} - {e.message}"
            )
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading {file.filename}: {e}")
            return None

    async def upload_stream(
        self, stream: BinaryIO, blob_path: str, content_type: str = "application/octet-stream"
    ) -> Optional[str]:
        """Upload a binary stream to Azure Blob Storage and return a SAS URL.

        Args:
            stream: Binary stream to upload
            blob_path: Destination path in the container
            content_type: MIME type of the content

        Returns:
            SAS URL if successful, None on error
        """
        if not self.connection_string:
            logger.error("Azure Storage connection string not configured")
            return None
        try:
            client = self._get_blob_service()
            self._ensure_container(client)
            container = client.get_container_client(self.container_name)
            blob_client = container.get_blob_client(blob_path)
            blob_client.upload_blob(stream, overwrite=True, content_type=content_type)
            return self._generate_sas_url(blob_path)
        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed uploading stream to {blob_path}: {e}")
            return None
        except HttpResponseError as e:
            logger.error(
                f"Azure service error uploading stream to {blob_path}: {e.status_code} - {e.message}"
            )
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading stream to {blob_path}: {e}")
            return None

    async def download_file(self, blob_path: str) -> Optional[bytes]:
        """Download a blob's content as bytes.

        Returns:
            bytes if successful, None if blob doesn't exist

        Raises:
            RuntimeError: For connection/auth errors (caller should handle)
        """
        if not self.connection_string:
            logger.error("Azure Storage connection string not configured")
            return None
        try:
            client = self._get_blob_service()
            container = client.get_container_client(self.container_name)
            blob_client = container.get_blob_client(blob_path)
            download_stream = blob_client.download_blob()
            content = download_stream.readall()
            logger.info(f"Successfully downloaded {blob_path}")
            return content
        except ResourceNotFoundError:
            # Blob doesn't exist - this is expected in many scenarios
            logger.info(f"Blob not found: {blob_path}")
            return None
        except ClientAuthenticationError as e:
            # Auth errors should not be retried - they need credential fixes
            logger.error(f"Authentication failed for {blob_path}: {e}")
            raise RuntimeError(f"Azure authentication failed: {e}") from e
        except HttpResponseError as e:
            # Other Azure service errors (rate limits, service issues, etc.)
            logger.error(
                f"Azure service error downloading {blob_path}: {e.status_code} - {e.message}"
            )
            raise RuntimeError(f"Azure Blob download failed for {blob_path}: {e.message}") from e
        except Exception as e:
            # Catch-all for unexpected errors (network, etc.)
            logger.error(f"Unexpected error downloading {blob_path}: {e}")
            raise RuntimeError(f"Unexpected error downloading {blob_path}: {e}") from e

    async def download_to_temp_file(self, blob_path: str) -> Optional[str]:
        """Download a blob to a temporary file and return its path."""
        content = await self.download_file(blob_path)
        if content is None:
            return None
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=os.path.splitext(blob_path)[1]
            ) as tf:
                tf.write(content)
                path = tf.name
            logger.info(f"Downloaded {blob_path} to temporary file: {path}")
            return path
        except Exception as e:
            logger.error(f"Failed to create temporary file for {blob_path}: {e}")
            return None

    def get_blob_url(self, blob_path: str, generate_sas: bool = True) -> Optional[str]:
        """Get a direct URL for a blob; optionally generate a SAS URL."""
        if generate_sas:
            try:
                return self._generate_sas_url(blob_path)
            except Exception as e:
                logger.error(f"Failed to generate SAS URL for {blob_path}: {e}")
                return None
        if self.base_blob_url:
            return f"{self.base_blob_url.rstrip('/')}/{blob_path}"
        logger.error("Cannot generate blob URL without base URL")
        return None

    async def delete_file(self, blob_path: str) -> bool:
        """Delete a blob and return True on success.

        Args:
            blob_path: Path to the blob to delete

        Returns:
            True if deleted successfully or blob doesn't exist, False on error
        """
        if not self.connection_string:
            logger.error("Azure Storage connection string not configured")
            return False
        try:
            client = self._get_blob_service()
            container = client.get_container_client(self.container_name)
            blob_client = container.get_blob_client(blob_path)
            blob_client.delete_blob()
            logger.info(f"Successfully deleted {blob_path}")
            return True
        except ResourceNotFoundError:
            # Blob already doesn't exist - this is still success
            logger.info(f"Blob {blob_path} already deleted or doesn't exist")
            return True
        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed when deleting {blob_path}: {e}")
            return False
        except HttpResponseError as e:
            logger.error(f"Azure service error deleting {blob_path}: {e.status_code} - {e.message}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting {blob_path}: {e}")
            return False

    async def file_exists(self, blob_path: str) -> bool:
        """Check if a blob exists in the container.

        Args:
            blob_path: Path to the blob to check

        Returns:
            True if blob exists, False otherwise (including on errors)
        """
        if not self.connection_string:
            logger.error("Azure Storage connection string not configured")
            return False
        try:
            client = self._get_blob_service()
            container = client.get_container_client(self.container_name)
            blob_client = container.get_blob_client(blob_path)
            return blob_client.exists()
        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed checking {blob_path}: {e}")
            return False
        except HttpResponseError as e:
            logger.error(f"Azure service error checking {blob_path}: {e.status_code} - {e.message}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking existence of {blob_path}: {e}")
            return False
