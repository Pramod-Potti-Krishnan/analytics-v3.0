"""
Supabase Storage integration for Analytics Microservice v3.
Handles uploading generated charts to Supabase Storage and returning public URLs.
"""

import logging
import uuid
from typing import Optional
from datetime import datetime
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseStorage:
    """Handles chart uploads to Supabase Storage."""

    def __init__(self, url: str, key: str, bucket_name: str = "analytics-charts"):
        """
        Initialize Supabase Storage client.

        Args:
            url: Supabase project URL
            key: Supabase service role key
            bucket_name: Storage bucket name
        """
        self.bucket_name = bucket_name
        self.client: Client = create_client(url, key)
        logger.info(f"Supabase Storage initialized for bucket: {bucket_name}")

    def create_bucket_if_not_exists(self) -> bool:
        """
        Create storage bucket if it doesn't exist.
        Sets bucket to public access for chart URLs.

        Returns:
            True if bucket exists or was created successfully
        """
        try:
            # Check if bucket exists
            buckets = self.client.storage.list_buckets()
            bucket_exists = any(b.name == self.bucket_name for b in buckets)

            if bucket_exists:
                logger.info(f"Bucket '{self.bucket_name}' already exists")
                return True

            # Create new bucket with public access
            self.client.storage.create_bucket(
                self.bucket_name,
                options={"public": True}
            )
            logger.info(f"Created new bucket: {self.bucket_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create bucket: {e}")
            return False

    def upload_chart(
        self,
        image_bytes: bytes,
        chart_type: str = "chart",
        file_extension: str = "png"
    ) -> Optional[str]:
        """
        Upload chart image to Supabase Storage.

        Args:
            image_bytes: PNG or SVG image bytes
            chart_type: Type of chart (for filename)
            file_extension: File extension (png or svg)

        Returns:
            Public URL of uploaded chart, or None if upload failed
        """
        try:
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_id = str(uuid.uuid4())[:8]
            filename = f"{chart_type}_{timestamp}_{chart_id}.{file_extension}"

            # Upload to Supabase Storage
            response = self.client.storage.from_(self.bucket_name).upload(
                path=filename,
                file=image_bytes,
                file_options={"content-type": f"image/{file_extension}"}
            )

            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(filename)

            logger.info(f"Chart uploaded successfully: {filename}")
            return public_url

        except Exception as e:
            logger.error(f"Failed to upload chart: {e}", exc_info=True)
            return None

    def delete_chart(self, filename: str) -> bool:
        """
        Delete a chart from storage.

        Args:
            filename: Name of file to delete

        Returns:
            True if deleted successfully
        """
        try:
            self.client.storage.from_(self.bucket_name).remove([filename])
            logger.info(f"Deleted chart: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete chart {filename}: {e}")
            return False

    def list_charts(self, limit: int = 100) -> list:
        """
        List charts in storage bucket.

        Args:
            limit: Maximum number of files to return

        Returns:
            List of file objects
        """
        try:
            files = self.client.storage.from_(self.bucket_name).list(
                path="",
                options={"limit": limit}
            )
            return files
        except Exception as e:
            logger.error(f"Failed to list charts: {e}")
            return []
