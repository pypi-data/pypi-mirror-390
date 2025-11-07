from typing import Annotated

from pydantic import AfterValidator, BaseModel, ValidationInfo, field_validator, model_validator
from pydantic_core import PydanticCustomError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.utils.pydantic.validators import non_blank


class ExcelMetadataFile(BaseModel):
    """Excel metadata configuration for base64 encoded data.

    This model is used specifically for base64-encoded Excel metadata files,
    typically from web frontends or API integrations.

    Attributes:
        data: Base64 encoded content of the Excel file
        filename: Name of the original file before base64 encoding

    Examples:
        Base64 mode:
            >>> config = ExcelMetadataFile(
            ...     data="UEsDBBQABgAI...",
            ...     filename="metadata.xlsx"
            ... )
    """

    data: str
    filename: str


class AssetConfig(BaseModel):
    """Configuration for individual asset in multi-path mode.

    Used when use_single_path=False to specify unique paths
    and recursive settings for each file specification.

    Attributes:
        path (str): File system path for this specific asset
        is_recursive (bool): Whether to recursively search subdirectories for this asset

    Example:
        >>> asset_config = AssetConfig(
        ...     path="/sensors/camera/front",
        ...     is_recursive=True
        ... )
    """

    path: str
    is_recursive: bool = True


class UploadParams(BaseModel):
    """Upload action parameter validation model.

    Defines and validates all parameters required for upload operations.
    Uses Pydantic for type validation and custom validators to ensure
    storage, data_collection, and project resources exist before processing.

    Supports two modes controlled by use_single_path flag:

    1. Single Path Mode (use_single_path=True, DEFAULT):
       Traditional mode - all file specifications share one base path.
       Requires: path, is_recursive
       Ignores: assets

    2. Multi-Path Mode (use_single_path=False):
       Advanced mode - each file specification has its own path.
       Requires: assets (dict with file spec names as keys)
       Ignores: path, is_recursive

    Attributes:
        name (str): Human-readable name for the upload operation
        description (str | None): Optional description of the upload
        use_single_path (bool): Mode selector (True=single path, False=multi-path)
        path (str | None): Base path for single path mode
        is_recursive (bool): Global recursive setting for single path mode
        assets (dict[str, AssetConfig] | None): Per-asset configs for multi-path mode
        storage (int): Storage ID where files will be uploaded
        data_collection (int): Data collection ID for organizing uploads
        project (int | None): Optional project ID for grouping
        excel_metadata_path (str | None): Path to Excel metadata file (traditional, backward compatible)
            Note: This parameter will be deprecated in a future version. Consider using excel_metadata instead.
        excel_metadata (ExcelMetadataFile | None): Base64 encoded Excel metadata (for web/API integration)
            Note: Cannot use both excel_metadata_path and excel_metadata simultaneously
        max_file_size_mb (int): Maximum file size limit in megabytes
        creating_data_unit_batch_size (int): Batch size for data unit creation
        use_async_upload (bool): Whether to use asynchronous upload processing
        extra_params (dict | None): Extra parameters for the action

    Validation:
        - name: Must be non-blank after validation
        - storage: Must exist and be accessible via client API
        - data_collection: Must exist and be accessible via client API
        - project: Must exist if specified, or can be None
        - use_single_path mode: Validates required fields per mode

    Examples:
        Single Path Mode (Traditional):
            >>> params = UploadParams(
            ...     name="Standard Upload",
            ...     use_single_path=True,
            ...     path="/data/experiment_1",
            ...     is_recursive=True,
            ...     storage=1,
            ...     data_collection=5
            ... )

        Multi-Path Mode (Advanced):
            >>> params = UploadParams(
            ...     name="Multi-Source Upload",
            ...     use_single_path=False,
            ...     assets={
            ...         "image_1": AssetConfig(path="/sensors/camera", is_recursive=True),
            ...         "pcd_1": AssetConfig(path="/sensors/lidar", is_recursive=False)
            ...     },
            ...     storage=1,
            ...     data_collection=5
            ... )
    """

    name: Annotated[str, AfterValidator(non_blank)]
    description: str | None = None

    # Mode selector flag (True = single path mode, False = multi-path mode)
    use_single_path: bool = True

    # Single path mode fields (used when use_single_path=True)
    path: str | None = None
    is_recursive: bool = True

    # Multi-path mode fields (used when use_single_path=False)
    assets: dict[str, AssetConfig] | None = None

    storage: int
    data_collection: int
    project: int | None = None

    # Excel metadata - two separate parameters for clarity:
    # 1. excel_metadata_path: Simple file path string (backward compatible, traditional usage)
    #    NOTE: Will be deprecated in a future version. Consider using excel_metadata instead.
    # 2. excel_metadata: Dictionary with base64 encoded data (new, for web/API integration)
    # TODO: Plan to deprecate excel_metadata_path in a few versions for backward compatibility
    excel_metadata_path: str | None = None
    excel_metadata: ExcelMetadataFile | None = None

    max_file_size_mb: int = 50
    creating_data_unit_batch_size: int = 1
    use_async_upload: bool = True
    extra_params: dict | None = None

    @field_validator('storage', mode='before')
    @classmethod
    def check_storage_exists(cls, value, info: ValidationInfo) -> int:
        if info.context is None:
            raise PydanticCustomError('missing_context', 'Validation context is required.')

        action = info.context['action']
        client = action.client
        try:
            client.get_storage(value)
        except ClientError:
            raise PydanticCustomError('client_error', 'Error occurred while checking storage exists.')
        return value

    @field_validator('data_collection', mode='before')
    @classmethod
    def check_data_collection_exists(cls, value, info: ValidationInfo) -> int:
        if info.context is None:
            raise PydanticCustomError('missing_context', 'Validation context is required.')

        action = info.context['action']
        client = action.client
        try:
            client.get_data_collection(value)
        except ClientError:
            raise PydanticCustomError('client_error', 'Error occurred while checking data_collection exists.')
        return value

    @field_validator('project', mode='before')
    @classmethod
    def check_project_exists(cls, value, info: ValidationInfo) -> int | None:
        if not value:
            return value

        if info.context is None:
            raise PydanticCustomError('missing_context', 'Validation context is required.')

        action = info.context['action']
        client = action.client
        try:
            client.get_project(value)
        except ClientError:
            raise PydanticCustomError('client_error', 'Error occurred while checking project exists.')
        return value

    @model_validator(mode='after')
    def validate_path_configuration(self) -> 'UploadParams':
        """Validate path configuration based on use_single_path mode."""
        if self.use_single_path:
            # Single path mode: requires path
            if not self.path:
                raise PydanticCustomError(
                    'missing_path', "When use_single_path=true (single path mode), 'path' is required"
                )
            # Warn if assets is provided in single path mode (it will be ignored)
            # For now, we'll silently ignore it
        else:
            # Multi-path mode: requires assets
            if not self.assets:
                raise PydanticCustomError(
                    'missing_assets',
                    "When use_single_path=false (multi-path mode), 'assets' must be provided "
                    'with path configurations for each file specification',
                )
            # path and is_recursive are ignored in multi-path mode

        # Validate excel metadata parameters - cannot use both at the same time
        if self.excel_metadata_path and self.excel_metadata:
            raise PydanticCustomError(
                'conflicting_excel_metadata',
                "Cannot specify both 'excel_metadata_path' and 'excel_metadata'. "
                "Use 'excel_metadata_path' for file paths or 'excel_metadata' for base64 encoded data.",
            )

        return self
