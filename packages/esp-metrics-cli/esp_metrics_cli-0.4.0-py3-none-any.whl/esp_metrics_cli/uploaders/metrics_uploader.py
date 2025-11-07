# SPDX-FileCopyrightText: 2025 Espressif Systems (Shanghai) CO LTD
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import time

from urllib.parse import urlparse

from esp_metrics_cli.clients.minio_client import MinioClient
from esp_metrics_cli.models.config import BucketType
from esp_metrics_cli.models.config import MetricsSettings
from esp_metrics_cli.models.result import UploadResult

logger = logging.getLogger(__name__)


class MetricsUploader:
    """Metrics uploader service that handles upload to S3 storage."""

    def __init__(self, settings: MetricsSettings, verbose: bool = False):
        """Initialize the uploader with settings and verbosity level."""
        self.settings = settings
        self.verbose = verbose
        self.minio_client = MinioClient(settings)

    def generate_object_name(self, metrics: dict) -> str:
        """Generate S3 object name from validated metrics data.

        Format: project_host/projectid_project_path/commit_sha/timestamp.json
        Example: https_gitlab.espressif.cn_6688/1111_espressif_esp-idf/commit_sha/2024-01-15_14-30-00.json
        """
        parsed_url = urlparse(metrics['project_url'])

        project_host = f'{parsed_url.scheme}_{parsed_url.netloc}'.replace(':', '_').replace('.', '_')

        project_path = parsed_url.path.lstrip('/').replace('/', '_')
        projectid_project_path = f'{metrics["project_id"]}_{project_path}'

        timestamp = metrics['timestamp'].replace(':', '-').replace('T', '_')
        return f'{project_host}/{projectid_project_path}/{metrics["commit_sha"]}/{timestamp}.json'

    def upload(
        self,
        data: dict,
        bucket_type: BucketType | str | None = None,
        custom_bucket: str | None = None,
    ) -> UploadResult:
        """Upload validated metrics to S3 storage."""
        start_time = time.time()
        result = UploadResult(is_validated=True)

        try:
            target_bucket = self.settings.get_target_bucket(bucket_type, custom_bucket)
            if self.verbose:
                logger.info(f'Bucket selection mode: {self.settings.metrics_upload_bucket_type}')
                logger.info(f'Target bucket: {target_bucket}')

            if not self.minio_client.client:
                result.upload_error = 'MinIO client not available - check S3 credentials'
                return result

            if not self.minio_client.bucket_exists(target_bucket):
                result.upload_error = f'Bucket {target_bucket} does not exist - check S3 configuration'
                return result

            object_name = self.generate_object_name(data)
            if self.verbose:
                logger.info(f'Generated object name: {object_name}')

            if self.verbose:
                logger.info(f'Uploading to bucket: {target_bucket}, object: {object_name}')

            self.minio_client.upload_json(target_bucket, object_name, data)

            result.bytes_uploaded = len(json.dumps(data).encode('utf-8'))

            result.upload_url = self.minio_client.generate_presigned_url(
                bucket=target_bucket,
                object_name=object_name,
            )

            result.upload_successful = True

            if self.verbose:
                logger.info('Upload completed successfully')
                logger.info(f'Upload URL: {result.upload_url}')
                logger.info(f'Bytes uploaded: {result.bytes_uploaded}')

        except Exception as e:
            logger.exception('Unexpected error during upload')
            result.upload_error = f'Upload failed: {e}'

        finally:
            result.upload_time = time.time() - start_time

        return result
