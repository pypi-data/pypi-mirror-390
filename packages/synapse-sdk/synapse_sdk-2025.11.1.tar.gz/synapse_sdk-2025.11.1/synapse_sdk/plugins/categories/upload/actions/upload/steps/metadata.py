import base64
import tempfile
from pathlib import Path

from ..context import StepResult, UploadContext
from ..enums import LogCode
from ..exceptions import ExcelParsingError, ExcelSecurityError
from ..models import ExcelMetadataFile
from .base import BaseStep


class ProcessMetadataStep(BaseStep):
    """Process metadata from Excel files or other sources."""

    @property
    def name(self) -> str:
        return 'process_metadata'

    @property
    def progress_weight(self) -> float:
        return 0.10

    def execute(self, context: UploadContext) -> StepResult:
        """Execute metadata processing step."""
        metadata_strategy = context.strategies.get('metadata')
        if not metadata_strategy:
            context.run.log_message('No metadata strategy configured - skipping metadata processing')
            return self.create_success_result(data={'metadata': {}})

        excel_metadata = {}
        temp_file_to_cleanup = None

        try:
            # Check if Excel metadata is specified - try both parameters
            # TODO: Plan to deprecate excel_metadata_path in a few versions (backward compatibility)
            excel_metadata_path_config = context.get_param('excel_metadata_path')
            excel_metadata_config = context.get_param('excel_metadata')

            if excel_metadata_path_config:
                # Traditional path-based approach (will be deprecated in future)
                excel_path, is_temp = self._resolve_excel_path_from_string(excel_metadata_path_config, context)

                if not excel_path or not excel_path.exists():
                    context.run.log_message_with_code(LogCode.EXCEL_FILE_NOT_FOUND_PATH)
                    return self.create_success_result(data={'metadata': {}})

                excel_metadata = metadata_strategy.extract(excel_path)

            elif excel_metadata_config:
                # Base64 encoded approach
                excel_path, is_temp = self._resolve_excel_path_from_base64(excel_metadata_config, context)

                if not excel_path or not excel_path.exists():
                    context.run.log_message_with_code(LogCode.EXCEL_FILE_NOT_FOUND_PATH)
                    return self.create_success_result(data={'metadata': {}})

                # Track temp file for cleanup
                if is_temp:
                    temp_file_to_cleanup = excel_path

                excel_metadata = metadata_strategy.extract(excel_path)
            else:
                # Look for default metadata files (meta.xlsx, meta.xls)
                # Only possible in single-path mode where pathlib_cwd is set
                if context.pathlib_cwd:
                    excel_path = self._find_excel_metadata_file(context.pathlib_cwd)
                    if excel_path:
                        excel_metadata = metadata_strategy.extract(excel_path)
                else:
                    context.run.log_message(
                        'No Excel metadata specified and multi-path mode - skipping metadata processing'
                    )

            # Validate extracted metadata
            if excel_metadata:
                validation_result = metadata_strategy.validate(excel_metadata)
                if not validation_result.valid:
                    error_msg = f'Metadata validation failed: {", ".join(validation_result.errors)}'
                    return self.create_error_result(error_msg)
                context.run.log_message_with_code(LogCode.EXCEL_METADATA_LOADED, len(excel_metadata))

            return self.create_success_result(
                data={'metadata': excel_metadata}, rollback_data={'metadata_processed': len(excel_metadata) > 0}
            )

        except ExcelSecurityError as e:
            context.run.log_message_with_code(LogCode.EXCEL_SECURITY_VIOLATION, str(e))
            return self.create_error_result(f'Excel security violation: {str(e)}')

        except ExcelParsingError as e:
            # If excel_metadata_path or excel_metadata was specified, this is an error
            # If we were just looking for default files, it's not an error
            if context.get_param('excel_metadata_path') or context.get_param('excel_metadata'):
                context.run.log_message_with_code(LogCode.EXCEL_PARSING_ERROR, str(e))
                return self.create_error_result(f'Excel parsing error: {str(e)}')
            else:
                context.run.log_message_with_code(LogCode.EXCEL_PARSING_ERROR, str(e))
                return self.create_success_result(data={'metadata': {}})

        except Exception as e:
            return self.create_error_result(f'Unexpected error processing metadata: {str(e)}')

        finally:
            # Clean up temporary file if it was created from base64
            if temp_file_to_cleanup and temp_file_to_cleanup.exists():
                try:
                    temp_file_to_cleanup.unlink()
                    context.run.log_message(f'Cleaned up temporary Excel file: {temp_file_to_cleanup}')
                except Exception as e:
                    context.run.log_message(f'Failed to clean up temporary file {temp_file_to_cleanup}: {str(e)}')

    def can_skip(self, context: UploadContext) -> bool:
        """Metadata step can be skipped if no metadata strategy is configured."""
        return 'metadata' not in context.strategies

    def rollback(self, context: UploadContext) -> None:
        """Rollback metadata processing."""
        # Clear any loaded metadata
        context.metadata.clear()

    def _resolve_excel_path_from_string(self, excel_path_str: str, context: UploadContext) -> tuple[Path | None, bool]:
        """Resolve Excel metadata path from a string path.

        Note: This method supports the excel_metadata_path parameter which will be deprecated
        in a future version. Consider using _resolve_excel_path_from_base64 instead.

        Args:
            excel_path_str: File path string to the Excel metadata file
            context: Upload context for resolving relative paths

        Returns:
            Tuple of (resolved_path, is_temporary_file)
            - resolved_path: Path object pointing to the Excel file, or None if resolution failed
            - is_temporary_file: Always False for path-based approach

        Examples:
            >>> path, is_temp = self._resolve_excel_path_from_string("/data/meta.xlsx", context)
        """
        # TODO: Plan to deprecate this method in a few versions (backward compatibility)
        # Try absolute path first
        path = Path(excel_path_str)
        if path.exists() and path.is_file():
            return path, False

        # Try relative to cwd (only if pathlib_cwd is set)
        if context.pathlib_cwd:
            path = context.pathlib_cwd / excel_path_str
            return (path, False) if path.exists() else (None, False)

        # In multi-path mode without pathlib_cwd, can only use absolute paths
        return (None, False)

    def _resolve_excel_path_from_base64(
        self, excel_config: dict | ExcelMetadataFile, context: UploadContext
    ) -> tuple[Path | None, bool]:
        """Resolve Excel metadata path from base64 encoded data.

        Args:
            excel_config: Either a dict or an ExcelMetadataFile object with base64 data
            context: Upload context for logging

        Returns:
            Tuple of (resolved_path, is_temporary_file)
            - resolved_path: Path object pointing to the temporary Excel file, or None if decoding failed
            - is_temporary_file: Always True for base64 approach (requires cleanup)

        Examples:
            >>> config = ExcelMetadataFile(data="UEsDB...", filename="meta.xlsx")
            >>> path, is_temp = self._resolve_excel_path_from_base64(config, context)
        """
        if isinstance(excel_config, dict):
            excel_config = ExcelMetadataFile(**excel_config)

        try:
            # Decode base64 data
            decoded_data = base64.b64decode(excel_config.data, validate=True)

            # Create temp file
            temp_dir = Path(tempfile.gettempdir())
            filename = excel_config.filename
            temp_file = temp_dir / filename
            temp_file.write_bytes(decoded_data)

            context.run.log_message(f'Decoded base64 Excel metadata to temporary file: {temp_file}')
            return temp_file, True

        except Exception as e:
            context.run.log_message(f'Failed to decode base64 Excel metadata: {str(e)}')
            return None, False

    def _find_excel_metadata_file(self, pathlib_cwd: Path) -> Path:
        """Find default Excel metadata file.

        Args:
            pathlib_cwd: Working directory path (must not be None)

        Returns:
            Path to Excel metadata file, or None if not found
        """
        if not pathlib_cwd:
            return None

        # Check .xlsx first as it's more common
        excel_path = pathlib_cwd / 'meta.xlsx'
        if excel_path.exists():
            return excel_path

        # Fallback to .xls
        excel_path = pathlib_cwd / 'meta.xls'
        if excel_path.exists():
            return excel_path

        return None
