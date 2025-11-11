"""Simple wrapper around boto3 S3 client."""

from typing import BinaryIO

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError, NoCredentialsError

from ..core.exception import RequestException
from ..log import footprint

__all__ = ("Bucket",)


class Bucket:
    """High level interface for reading/writing files to S3 compatible
    storage."""

    def __init__(
        self,
        name: str | None = None,
        s3_mode: str | None = None,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        region_name: str | None = None,
    ) -> None:
        """Initialize S3-compatible bucket client.

        Args:
            name: Name of the S3 bucket.
            s3_mode: Flag to enable AWS S3 mode (as opposed to S3-compatible storage).
            endpoint_url: Custom endpoint URL for S3-compatible storage.
            access_key: AWS access key ID or equivalent.
            secret_key: AWS secret access key or equivalent.
            region_name: AWS region name for S3 mode.
        """
        footprint.leave(
            log_type="debug",
            controller=f"{__name__}.Bucket.__init__",
            message="Initializing Bucket",
            payload={
                "name": name,
                "s3_mode": s3_mode,
                "endpoint_url": endpoint_url,
                "region_name": region_name,
            },
        )
        self.__name = name
        self.__s3_mode = bool(s3_mode)
        self.__endpoint_url = endpoint_url
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.__region_name = region_name
        self.__s3_client: BaseClient = boto3.client(
            "s3",
            aws_access_key_id=self.__access_key,
            aws_secret_access_key=self.__secret_key,
            endpoint_url=self.__endpoint_url if not self.__s3_mode else None,
            region_name=self.__region_name if self.__s3_mode else None,
        )

    def url_generator(self, key: str) -> str:
        """Generate the public URL for an object in the bucket.

        Args:
            key: Object key/path within the bucket.

        Returns:
            Public URL string for accessing the object.
        """
        footprint.leave(
            log_type="debug",
            controller=f"{__name__}.Bucket.url_generator",
            message=f"Generating URL for key: {key}",
            payload={"key": key},
        )

        if self.__s3_mode:
            return f"{self.__endpoint_url}/{key}"
        else:
            return f"{self.__endpoint_url}/{self.__name}/{key}"

    def get_s3(self) -> BaseClient:
        """Get the underlying boto3 S3 client instance.

        Returns:
            The boto3 BaseClient for S3 operations.
        """
        footprint.leave(
            log_type="debug",
            controller=f"{__name__}.Bucket.get_s3",
            message="Getting S3 client",
        )

        return self.__s3_client

    def get_bucket_name(self) -> str | None:
        """Get the configured bucket name.

        Returns:
            The bucket name if configured, otherwise None.
        """
        footprint.leave(
            log_type="debug",
            controller=f"{__name__}.Bucket.get_bucket_name",
            message="Getting bucket name",
        )

        return self.__name

    def check_file_exists(self, key: str) -> bool:
        """Check if an object exists in the bucket.

        Args:
            key: Object key/path to check for existence.

        Returns:
            True if the object exists, False otherwise.
        """
        footprint.leave(
            log_type="debug",
            controller=f"{__name__}.Bucket.check_file_exists",
            message=f"Checking if file exists: {key}",
            payload={"key": key},
        )
        controller = f"{__name__}.Bucket.check_file_exists"
        try:
            self.__s3_client.head_object(Bucket=self.__name, Key=key)
            return True
        except NoCredentialsError:
            raise RequestException(
                controller=controller,
                message="S3 credentials error",
                status_code=500,
            )
        except Exception:
            return False

    def upload(
        self, file: bytes, key: str, content_type: str, cache_control: str = "no-cache"
    ) -> str:
        """Upload bytes content to the bucket.

        Args:
            file: Binary content to upload.
            key: Object key/path for the uploaded content.
            content_type: MIME type of the content.
            cache_control: Cache control header value (default: "no-cache").

        Returns:
            Public URL of the uploaded object.
        """
        footprint.leave(
            log_type="debug",
            controller=f"{__name__}.Bucket.upload",
            message=f"Uploading file to key: {key}",
            payload={
                "key": key,
                "content_type": content_type,
                "cache_control": cache_control,
            },
        )
        controller = f"{__name__}.Bucket.upload"
        try:
            self.__s3_client.put_object(
                Body=file,
                Bucket=self.__name,
                Key=key,
                ContentType=content_type,
                CacheControl=cache_control,
            )
        except NoCredentialsError:
            raise RequestException(
                controller=controller,
                message="S3 credentials error",
                status_code=500,
            )
        return self.url_generator(key=key)

    def download(self, key: str, filepath: str) -> bool:
        """Download an object from the bucket to a local file.

        Args:
            key: Object key/path to download.
            filepath: Local filesystem path where the file will be saved.

        Returns:
            True if download succeeded.
        """
        footprint.leave(
            log_type="debug",
            controller=f"{__name__}.Bucket.download",
            message=f"Downloading file from key: {key} to {filepath}",
            payload={"key": key, "filepath": filepath},
        )
        controller = f"{__name__}.Bucket.download"
        try:
            self.__s3_client.download_file(
                Bucket=self.__name,
                Key=key,
                Filename=filepath,
            )
        except NoCredentialsError:
            raise RequestException(
                controller=controller,
                message="S3 credentials error",
                status_code=500,
            )
        return True

    def download_fileobj(self, key: str, file: BinaryIO) -> bool:
        """Download an object from the bucket into an open file object.

        Args:
            key: Object key/path to download.
            file: Open file object to write the downloaded content into.

        Returns:
            True if download succeeded.
        """
        footprint.leave(
            log_type="debug",
            controller=f"{__name__}.Bucket.download_fileobj",
            message=f"Downloading file from key: {key} to file object",
            payload={"key": key},
        )
        controller = f"{__name__}.Bucket.download_fileobj"
        try:
            self.__s3_client.download_fileobj(
                Bucket=self.__name,
                Key=key,
                Fileobj=file,
            )
        except NoCredentialsError:
            raise RequestException(
                controller=controller,
                message="S3 credentials error",
                status_code=500,
            )
        return True

    def upload_by_path(
        self,
        file_path: str,
        key: str,
        content_type: str | None = None,
        cache_control: str = "no-cache",
    ) -> str:
        """Upload a file from the local filesystem to the bucket.

        Args:
            file_path: Local filesystem path to the file to upload.
            key: Object key/path for the uploaded content.
            content_type: MIME type of the content (default: "application/octet-stream").
            cache_control: Cache control header value (default: "no-cache").

        Returns:
            Public URL of the uploaded object.
        """
        footprint.leave(
            log_type="debug",
            controller=f"{__name__}.Bucket.upload_by_path",
            message=f"Uploading file from path: {file_path} to key: {key}",
            payload={
                "file_path": file_path,
                "key": key,
                "content_type": content_type,
                "cache_control": cache_control,
            },
        )
        controller = f"{__name__}.Bucket.upload_by_path"
        try:
            with open(file_path, "rb") as file:
                file_content = file.read()
                content_type = content_type or "application/octet-stream"
                return self.upload(
                    file=file_content,
                    key=key,
                    content_type=content_type,
                    cache_control=cache_control,
                )
        except NoCredentialsError:
            raise RequestException(
                controller=controller,
                message="S3 credentials error",
                status_code=500,
            )

    def duplicate(
        self, source_key: str, destination_key: str, cache_control: str = "no-cache"
    ) -> str:
        """Duplicate an object within the bucket.

        Args:
            source_key: Object key/path to copy from.
            destination_key: Object key/path to copy to.
            cache_control: Cache control header value (default: "no-cache").

        Returns:
            Public URL of the duplicated object.
        """
        footprint.leave(
            log_type="debug",
            controller=f"{__name__}.Bucket.duplicate",
            message=f"Duplicating file from {source_key} to {destination_key}",
            payload={
                "source_key": source_key,
                "destination_key": destination_key,
                "cache_control": cache_control,
            },
        )
        controller = f"{__name__}.Bucket.duplicate"
        try:
            self.__s3_client.copy(
                CopySource={"Bucket": self.__name, "Key": source_key},
                Bucket=self.__name,
                Key=destination_key,
                ExtraArgs={"CacheControl": cache_control},
            )
        except NoCredentialsError:
            raise RequestException(
                controller=controller,
                message="S3 credentials error",
                status_code=500,
            )
        return self.url_generator(key=destination_key)

    def safe_duplicate(self, source_key: str, cache_control: str = "no-cache") -> str:
        """Duplicate an object avoiding name collisions by appending a counter.

        Args:
            source_key: Object key/path to copy from.
            cache_control: Cache control header value (default: "no-cache").

        Returns:
            Public URL of the duplicated object with a unique key.
        """
        footprint.leave(
            log_type="debug",
            controller=f"{__name__}.Bucket.safe_duplicate",
            message=f"Safely duplicating file from {source_key}",
            payload={"source_key": source_key, "cache_control": cache_control},
        )
        controller = f"{__name__}.Bucket.safe_duplicate"
        try:
            default_key = source_key
            key = default_key
            i = 2
            while self.check_file_exists(key):
                name, ext = default_key.rsplit(".", 1)
                key = f"{name}-{i}.{ext}"
                i += 1
        except NoCredentialsError:
            raise RequestException(
                controller=controller,
                message="S3 credentials error",
                status_code=500,
            )

        return self.duplicate(
            source_key=source_key, destination_key=key, cache_control=cache_control
        )

    def delete(self, key: str) -> bool:
        """Delete an object from the bucket.

        Args:
            key: Object key/path to delete.

        Returns:
            True if the object was deleted or did not exist.
        """
        footprint.leave(
            log_type="debug",
            controller=f"{__name__}.Bucket.delete",
            message=f"Deleting file with key: {key}",
            payload={"key": key},
        )
        controller = f"{__name__}.Bucket.delete"
        try:
            self.__s3_client.delete_object(Bucket=self.__name, Key=key)
            return True
        except NoCredentialsError:
            raise RequestException(
                controller=controller,
                message="S3 credentials error",
                status_code=500,
            )
        except ClientError:
            return True
