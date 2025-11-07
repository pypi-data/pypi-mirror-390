from enum import Enum

from synapse_sdk.shared.enums import Context


class UploadStatus(str, Enum):
    """Upload processing status enumeration.

    Defines the possible states for upload operations, data files, and data units
    throughout the upload process.

    Attributes:
        SUCCESS: Upload completed successfully
        FAILED: Upload failed with errors
    """

    SUCCESS = 'success'
    FAILED = 'failed'


class LogCode(str, Enum):
    """Type-safe logging codes for upload operations.

    Enumeration of all possible log events during upload processing. Each code
    corresponds to a specific event or error state with predefined message
    templates and log levels.

    The codes are organized by category:
    - Validation codes (VALIDATION_FAILED, STORAGE_VALIDATION_FAILED, etc.)
    - File processing codes (NO_FILES_FOUND, FILES_DISCOVERED, etc.)
    - Excel processing codes (EXCEL_SECURITY_VIOLATION, EXCEL_PARSING_ERROR, etc.)
    - Progress tracking codes (UPLOADING_DATA_FILES, GENERATING_DATA_UNITS, etc.)

    Each code maps to a configuration in LOG_MESSAGES with message template
    and appropriate log level.
    """

    STORAGE_VALIDATION_FAILED = 'STORAGE_VALIDATION_FAILED'
    COLLECTION_VALIDATION_FAILED = 'COLLECTION_VALIDATION_FAILED'
    PROJECT_VALIDATION_FAILED = 'PROJECT_VALIDATION_FAILED'
    VALIDATION_FAILED = 'VALIDATION_FAILED'
    NO_FILES_FOUND = 'NO_FILES_FOUND'
    NO_FILES_UPLOADED = 'NO_FILES_UPLOADED'
    NO_DATA_UNITS_GENERATED = 'NO_DATA_UNITS_GENERATED'
    NO_TYPE_DIRECTORIES = 'NO_TYPE_DIRECTORIES'
    EXCEL_SECURITY_VIOLATION = 'EXCEL_SECURITY_VIOLATION'
    EXCEL_PARSING_ERROR = 'EXCEL_PARSING_ERROR'
    EXCEL_METADATA_LOADED = 'EXCEL_METADATA_LOADED'
    UPLOADING_DATA_FILES = 'UPLOADING_DATA_FILES'
    GENERATING_DATA_UNITS = 'GENERATING_DATA_UNITS'
    IMPORT_COMPLETED = 'IMPORT_COMPLETED'
    TYPE_DIRECTORIES_FOUND = 'TYPE_DIRECTORIES_FOUND'
    TYPE_STRUCTURE_DETECTED = 'TYPE_STRUCTURE_DETECTED'
    FILES_DISCOVERED = 'FILES_DISCOVERED'
    NO_FILES_FOUND_WARNING = 'NO_FILES_FOUND_WARNING'
    FILE_UPLOAD_FAILED = 'FILE_UPLOAD_FAILED'
    DATA_UNIT_BATCH_FAILED = 'DATA_UNIT_BATCH_FAILED'
    FILENAME_TOO_LONG = 'FILENAME_TOO_LONG'
    MISSING_REQUIRED_FILES = 'MISSING_REQUIRED_FILES'
    EXCEL_FILE_NOT_FOUND = 'EXCEL_FILE_NOT_FOUND'
    EXCEL_FILE_VALIDATION_STARTED = 'EXCEL_FILE_VALIDATION_STARTED'
    EXCEL_WORKBOOK_LOADED = 'EXCEL_WORKBOOK_LOADED'
    FILE_ORGANIZATION_STARTED = 'FILE_ORGANIZATION_STARTED'
    BATCH_PROCESSING_STARTED = 'BATCH_PROCESSING_STARTED'
    EXCEL_SECURITY_VALIDATION_STARTED = 'EXCEL_SECURITY_VALIDATION_STARTED'
    EXCEL_MEMORY_ESTIMATION = 'EXCEL_MEMORY_ESTIMATION'
    EXCEL_FILE_NOT_FOUND_PATH = 'EXCEL_FILE_NOT_FOUND_PATH'
    EXCEL_SECURITY_VALIDATION_FAILED = 'EXCEL_SECURITY_VALIDATION_FAILED'
    EXCEL_PARSING_FAILED = 'EXCEL_PARSING_FAILED'
    EXCEL_INVALID_FILE_FORMAT = 'EXCEL_INVALID_FILE_FORMAT'
    EXCEL_FILE_TOO_LARGE = 'EXCEL_FILE_TOO_LARGE'
    EXCEL_FILE_ACCESS_ERROR = 'EXCEL_FILE_ACCESS_ERROR'
    EXCEL_UNEXPECTED_ERROR = 'EXCEL_UNEXPECTED_ERROR'


LOG_MESSAGES = {
    LogCode.STORAGE_VALIDATION_FAILED: {
        'message': 'Storage validation failed.',
        'level': Context.DANGER,
    },
    LogCode.COLLECTION_VALIDATION_FAILED: {
        'message': 'Collection validation failed.',
        'level': Context.DANGER,
    },
    LogCode.PROJECT_VALIDATION_FAILED: {
        'message': 'Project validation failed.',
        'level': Context.DANGER,
    },
    LogCode.VALIDATION_FAILED: {
        'message': 'Validation failed.',
        'level': Context.DANGER,
    },
    LogCode.NO_FILES_FOUND: {
        'message': 'Files not found on the path.',
        'level': Context.WARNING,
    },
    LogCode.NO_FILES_UPLOADED: {
        'message': 'No files were uploaded.',
        'level': Context.WARNING,
    },
    LogCode.NO_DATA_UNITS_GENERATED: {
        'message': 'No data units were generated.',
        'level': Context.WARNING,
    },
    LogCode.NO_TYPE_DIRECTORIES: {
        'message': 'No type-based directory structure found.',
        'level': Context.INFO,
    },
    LogCode.EXCEL_SECURITY_VIOLATION: {
        'message': 'Excel security validation failed: {}',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_PARSING_ERROR: {
        'message': 'Excel parsing failed: {}',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_METADATA_LOADED: {
        'message': 'Excel metadata loaded for {} files',
        'level': None,
    },
    LogCode.UPLOADING_DATA_FILES: {
        'message': 'Uploading data files...',
        'level': None,
    },
    LogCode.GENERATING_DATA_UNITS: {
        'message': 'Generating data units...',
        'level': None,
    },
    LogCode.IMPORT_COMPLETED: {
        'message': 'Import completed.',
        'level': None,
    },
    LogCode.TYPE_DIRECTORIES_FOUND: {
        'message': 'Found type directories: {}',
        'level': None,
    },
    LogCode.TYPE_STRUCTURE_DETECTED: {
        'message': 'Detected type-based directory structure',
        'level': None,
    },
    LogCode.FILES_DISCOVERED: {
        'message': 'Discovered {} files',
        'level': None,
    },
    LogCode.NO_FILES_FOUND_WARNING: {
        'message': 'No files found.',
        'level': Context.WARNING,
    },
    LogCode.FILE_UPLOAD_FAILED: {
        'message': 'Failed to upload file: {}',
        'level': Context.DANGER,
    },
    LogCode.DATA_UNIT_BATCH_FAILED: {
        'message': 'Failed to create data units batch: {}',
        'level': Context.DANGER,
    },
    LogCode.FILENAME_TOO_LONG: {
        'message': 'Skipping file with overly long name: {}...',
        'level': Context.WARNING,
    },
    LogCode.MISSING_REQUIRED_FILES: {
        'message': '{} missing required files: {}',
        'level': Context.WARNING,
    },
    LogCode.EXCEL_FILE_NOT_FOUND: {
        'message': 'Excel metadata file not found: {}',
        'level': Context.WARNING,
    },
    LogCode.EXCEL_FILE_VALIDATION_STARTED: {
        'message': 'Excel file validation started',
        'level': Context.INFO,
    },
    LogCode.EXCEL_WORKBOOK_LOADED: {
        'message': 'Excel workbook loaded successfully',
        'level': Context.INFO,
    },
    LogCode.FILE_ORGANIZATION_STARTED: {
        'message': 'File organization started',
        'level': Context.INFO,
    },
    LogCode.BATCH_PROCESSING_STARTED: {
        'message': 'Batch processing started: {} batches of {} items each',
        'level': Context.INFO,
    },
    LogCode.EXCEL_SECURITY_VALIDATION_STARTED: {
        'message': 'Excel security validation started for file size: {} bytes',
        'level': Context.INFO,
    },
    LogCode.EXCEL_MEMORY_ESTIMATION: {
        'message': 'Excel memory estimation: {} bytes (file) * 3 = {} bytes (estimated)',
        'level': Context.INFO,
    },
    LogCode.EXCEL_FILE_NOT_FOUND_PATH: {
        'message': 'Excel metadata file not found',
        'level': Context.WARNING,
    },
    LogCode.EXCEL_SECURITY_VALIDATION_FAILED: {
        'message': 'Excel security validation failed: {}',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_PARSING_FAILED: {
        'message': 'Excel parsing failed: {}',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_INVALID_FILE_FORMAT: {
        'message': 'Invalid Excel file format: {}',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_FILE_TOO_LARGE: {
        'message': 'Excel file too large to process (memory limit exceeded)',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_FILE_ACCESS_ERROR: {
        'message': 'File access error reading excel metadata: {}',
        'level': Context.DANGER,
    },
    LogCode.EXCEL_UNEXPECTED_ERROR: {
        'message': 'Unexpected error reading excel metadata: {}',
        'level': Context.DANGER,
    },
}
