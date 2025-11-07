import base64
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.plugins.categories.upload.actions.upload import ExcelMetadataFile, UploadParams


class TestUploadParams:
    """Test UploadParams pydantic model."""

    def test_upload_params_creation_valid(self):
        """Test creating UploadParams with valid data."""

        # Mock action with client for validators
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_client.get_project.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {
                'name': 'Test Upload',
                'description': 'Test description',
                'path': '/test/path',
                'storage': 1,
                'data_collection': 1,
                'project': 1,
                'excel_metadata_path': 'tests/test_data/metadata.xlsx',
                'is_recursive': True,
                'max_file_size_mb': 100,
                'creating_data_unit_batch_size': 200,
                'use_async_upload': False,
            },
            context=context,
        )

        assert params.name == 'Test Upload'
        assert params.description == 'Test description'
        assert params.path == '/test/path'
        assert params.storage == 1
        assert params.data_collection == 1
        assert params.project == 1
        assert params.excel_metadata_path == 'tests/test_data/metadata.xlsx'
        assert params.is_recursive is True
        assert params.max_file_size_mb == 100
        assert params.creating_data_unit_batch_size == 200
        assert params.use_async_upload is False

    def test_upload_params_creation_minimal(self):
        """Test creating UploadParams with minimal required fields."""

        # Mock action with client for validators
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}, context=context
        )

        assert params.name == 'Test Upload'
        assert params.description is None
        assert params.path == '/test/path'
        assert params.storage == 1
        assert params.data_collection == 1
        assert params.project is None
        assert params.excel_metadata is None
        assert params.is_recursive is True
        assert params.max_file_size_mb == 50
        assert params.creating_data_unit_batch_size == 1
        assert params.use_async_upload is True

    def test_upload_params_blank_name_validation(self):
        """Test UploadParams validation fails with blank name."""

        # Mock action with client
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        with pytest.raises(ValidationError) as exc_info:
            UploadParams.model_validate(
                {
                    'name': '',  # Blank name should fail
                    'path': '/test/path',
                    'storage': 1,
                    'data_collection': 1,
                },
                context=context,
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error['loc'] == ('name',) for error in errors)

    def test_upload_params_storage_validation_success(self):
        """Test storage validation passes when storage exists."""

        # Mock action with client that returns storage
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}, context=context
        )

        assert params.storage == 1
        mock_client.get_storage.assert_called_once_with(1)

    def test_upload_params_storage_validation_failure(self):
        """Test storage validation fails when storage doesn't exist."""

        # Mock action with client that raises ClientError
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.side_effect = ClientError(status=404, reason='Storage not found')
        mock_action.client = mock_client

        context = {'action': mock_action}

        with pytest.raises(ValidationError) as exc_info:
            UploadParams.model_validate(
                {
                    'name': 'Test Upload',
                    'path': '/test/path',
                    'storage': 999,  # Non-existent storage
                    'data_collection': 1,
                },
                context=context,
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error['loc'] == ('storage',) for error in errors)

    def test_upload_params_collection_validation_success(self):
        """Test collection validation passes when collection exists."""

        # Mock action with client that returns collection
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}, context=context
        )

        assert params.data_collection == 1
        mock_client.get_data_collection.assert_called_once_with(1)

    def test_upload_params_collection_validation_failure(self):
        """Test collection validation fails when collection doesn't exist."""

        # Mock action with client that raises ClientError for collection
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.side_effect = ClientError(status=404, reason='Collection not found')
        mock_action.client = mock_client

        context = {'action': mock_action}

        with pytest.raises(ValidationError) as exc_info:
            UploadParams.model_validate(
                {
                    'name': 'Test Upload',
                    'path': '/test/path',
                    'storage': 1,
                    'data_collection': 999,  # Non-existent collection
                },
                context=context,
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error['loc'] == ('data_collection',) for error in errors)

    def test_upload_params_project_validation_success(self):
        """Test project validation passes when project exists."""

        # Mock action with client that returns project
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_client.get_project.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1, 'project': 1},
            context=context,
        )

        assert params.project == 1
        mock_client.get_project.assert_called_once_with(1)

    def test_upload_params_project_validation_none(self):
        """Test project validation when project is None."""

        # Mock action with client
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1, 'project': None},
            context=context,
        )

        assert params.project is None
        # get_project should not be called when project is None
        mock_client.get_project.assert_not_called()

    def test_excel_metadata_path_with_string(self):
        """Test excel_metadata_path accepts string path (backward compatibility)."""
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {
                'name': 'Test Upload',
                'path': '/test/path',
                'storage': 1,
                'data_collection': 1,
                'excel_metadata_path': '/path/to/metadata.xlsx',
            },
            context=context,
        )

        assert params.excel_metadata_path == '/path/to/metadata.xlsx'
        assert isinstance(params.excel_metadata_path, str)
        assert params.excel_metadata is None

    def test_excel_metadata_with_base64(self):
        """Test excel_metadata with base64 encoded data."""
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        # Create a sample base64 encoded string
        test_data = b'Test Excel File Content'
        encoded_data = base64.b64encode(test_data).decode('utf-8')

        params = UploadParams.model_validate(
            {
                'name': 'Test Upload',
                'path': '/test/path',
                'storage': 1,
                'data_collection': 1,
                'excel_metadata': {'data': encoded_data, 'filename': 'metadata.xlsx'},
            },
            context=context,
        )

        assert isinstance(params.excel_metadata, ExcelMetadataFile)
        assert params.excel_metadata.data == encoded_data
        assert params.excel_metadata.filename == 'metadata.xlsx'
        assert params.excel_metadata_path is None

    def test_excel_metadata_both_none(self):
        """Test both excel_metadata_path and excel_metadata can be None (optional fields)."""
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        params = UploadParams.model_validate(
            {
                'name': 'Test Upload',
                'path': '/test/path',
                'storage': 1,
                'data_collection': 1,
            },
            context=context,
        )

        assert params.excel_metadata_path is None
        assert params.excel_metadata is None

    def test_excel_metadata_conflicting_parameters(self):
        """Test that using both excel_metadata_path and excel_metadata raises error."""
        mock_action = Mock()
        mock_client = Mock()
        mock_client.get_storage.return_value = {'id': 1}
        mock_client.get_data_collection.return_value = {'id': 1}
        mock_action.client = mock_client

        context = {'action': mock_action}

        # Create a sample base64 encoded string
        test_data = b'Test Excel File Content'
        encoded_data = base64.b64encode(test_data).decode('utf-8')

        with pytest.raises(ValidationError) as exc_info:
            UploadParams.model_validate(
                {
                    'name': 'Test Upload',
                    'path': '/test/path',
                    'storage': 1,
                    'data_collection': 1,
                    'excel_metadata_path': '/path/to/metadata.xlsx',
                    'excel_metadata': {'data': encoded_data, 'filename': 'metadata.xlsx'},
                },
                context=context,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['type'] == 'conflicting_excel_metadata'


class TestExcelMetadataFile:
    """Test ExcelMetadataFile model."""

    def test_excel_metadata_file_base64_mode(self):
        """Test ExcelMetadataFile with base64 data and filename."""
        test_data = b'Test Excel Content'
        encoded = base64.b64encode(test_data).decode('utf-8')

        config = ExcelMetadataFile(data=encoded, filename='meta.xlsx')
        assert config.data == encoded
        assert config.filename == 'meta.xlsx'

    def test_excel_metadata_file_requires_filename(self):
        """Test ExcelMetadataFile requires filename field."""
        test_data = b'Test Excel Content'
        encoded = base64.b64encode(test_data).decode('utf-8')

        # Should fail - filename is required
        with pytest.raises(ValidationError) as exc_info:
            ExcelMetadataFile(data=encoded)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]['type'] == 'missing'
        assert 'filename' in str(errors[0])
