import asyncio
from pathlib import Path
from typing import Any, Dict, List

from synapse_sdk.clients.exceptions import ClientError

from ...enums import LogCode, UploadStatus
from ..base import UploadConfig, UploadStrategy


class AsyncUploadStrategy(UploadStrategy):
    """Asynchronous upload strategy."""

    def __init__(self, context):
        self.context = context

    def upload(self, files: List[Dict], config: UploadConfig) -> List[Dict]:
        """Upload files asynchronously."""
        # Use the run_async helper from the action
        return self._run_async_upload(files, config)

    def _run_async_upload(self, files: List[Dict], config: UploadConfig) -> List[Dict]:
        """Run async upload using asyncio."""
        import concurrent.futures

        def _run_in_thread():
            return asyncio.run(self._upload_files_async(files, config))

        try:
            # Check if we're already in an event loop
            asyncio.get_running_loop()
            # If we are, run in a separate thread
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_run_in_thread)
                return future.result()
        except RuntimeError:
            # No event loop running, safe to run directly
            return asyncio.run(self._upload_files_async(files, config))

    async def _upload_files_async(self, organized_files: List[Dict], config: UploadConfig) -> List[Dict]:
        """Upload files asynchronously with concurrency control."""
        client = self.context.client
        collection_id = self.context.get_param('data_collection')
        upload_result = []

        semaphore = asyncio.Semaphore(config.max_concurrent)

        async def upload_single_file(organized_file):
            async with semaphore:
                loop = asyncio.get_event_loop()
                try:
                    use_chunked_upload = self._requires_chunked_upload(organized_file, config)
                    uploaded_data_file = await loop.run_in_executor(
                        None, lambda: client.upload_data_file(organized_file, collection_id, use_chunked_upload)
                    )
                    self.context.run.log_data_file(organized_file, UploadStatus.SUCCESS)
                    return {'status': 'success', 'result': uploaded_data_file}
                except ClientError as e:
                    self.context.run.log_data_file(organized_file, UploadStatus.FAILED)
                    self.context.run.log_message_with_code(LogCode.FILE_UPLOAD_FAILED, f'Client error: {str(e)}')
                    return {'status': 'failed', 'error': str(e), 'error_type': 'client_error', 'retryable': True}
                except (OSError, IOError) as e:
                    self.context.run.log_data_file(organized_file, UploadStatus.FAILED)
                    self.context.run.log_message_with_code(LogCode.FILE_UPLOAD_FAILED, f'File system error: {str(e)}')
                    return {'status': 'failed', 'error': str(e), 'error_type': 'file_error', 'retryable': False}
                except MemoryError as e:
                    self.context.run.log_data_file(organized_file, UploadStatus.FAILED)
                    self.context.run.log_message_with_code(
                        LogCode.FILE_UPLOAD_FAILED, f'Memory error (file too large): {str(e)}'
                    )
                    return {'status': 'failed', 'error': str(e), 'error_type': 'memory_error', 'retryable': False}
                except asyncio.TimeoutError as e:
                    self.context.run.log_data_file(organized_file, UploadStatus.FAILED)
                    self.context.run.log_message_with_code(LogCode.FILE_UPLOAD_FAILED, f'Upload timeout: {str(e)}')
                    return {'status': 'failed', 'error': str(e), 'error_type': 'timeout_error', 'retryable': True}
                except ValueError as e:
                    self.context.run.log_data_file(organized_file, UploadStatus.FAILED)
                    self.context.run.log_message_with_code(
                        LogCode.FILE_UPLOAD_FAILED, f'Data validation error: {str(e)}'
                    )
                    return {'status': 'failed', 'error': str(e), 'error_type': 'validation_error', 'retryable': False}
                except Exception as e:
                    self.context.run.log_data_file(organized_file, UploadStatus.FAILED)
                    self.context.run.log_message_with_code(LogCode.FILE_UPLOAD_FAILED, f'Unexpected error: {str(e)}')
                    return {'status': 'failed', 'error': str(e), 'error_type': 'unknown_error', 'retryable': False}

        # Create tasks for all files
        tasks = [upload_single_file(organized_file) for organized_file in organized_files]

        # Process completed tasks
        for completed_task in asyncio.as_completed(tasks):
            result = await completed_task
            if result['status'] == 'success':
                upload_result.append(result['result'])
            # Failed uploads are logged but don't stop the process

        return upload_result

    def _requires_chunked_upload(self, organized_file: Dict[str, Any], config: UploadConfig) -> bool:
        """Determine if chunked upload is required based on file sizes."""
        max_file_size_mb = config.chunked_threshold_mb
        for file_path in organized_file.get('files', {}).values():
            if isinstance(file_path, Path) and self._get_file_size_mb(file_path) > max_file_size_mb:
                return True
        return False

    def _get_file_size_mb(self, file_path: Path) -> float:
        """Get file size in megabytes."""
        return file_path.stat().st_size / (1024 * 1024)
