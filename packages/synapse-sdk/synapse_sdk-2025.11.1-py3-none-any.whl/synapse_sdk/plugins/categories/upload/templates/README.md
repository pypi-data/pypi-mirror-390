# Upload Plugin

The Upload Plugin provides comprehensive file and data upload functionality with support for various storage backends, flexible asset path configuration, and Excel metadata integration.

## Quick Start Usage

### CLI Usage Examples

#### Standard Upload (Single Directory)

```bash
synapse plugin run upload '{
  "name": "Dataset Upload",
  "storage": 1,
  "collection": 2,
  "use_single_path": false,
  "assets": {
    "path": "/data/dataset",
    "recursive": true
  }
}'
```

#### Multi-Path Upload (Different Locations)

```bash
synapse plugin run upload '{
  "name": "Complex Dataset Upload",
  "storage": 1,
  "collection": 2,
  "use_single_path": true,
  "assets": {
    "images": {"path": "/images", "recursive": true},
    "pointclouds": {"path": "/pcd", "recursive": false},
    "annotations": {"path": "/labels", "recursive": true}
  },
  "excel_metadata_path": "/metadata/dataset_info.xlsx"
}' --debug
```

### Common Use Cases

#### 1. Simple Dataset Upload

```json
{
  "name": "Training Dataset",
  "storage": 1,
  "collection": 2,
  "assets": {
    "path": "/datasets/training",
    "recursive": true
  }
}
```

#### 2. Multi-Source Dataset Upload

```json
{
  "name": "Multi-Camera Dataset",
  "storage": 1,
  "collection": 2,
  "use_single_path": true,
  "assets": {
    "front_camera": { "path": "/cameras/front", "recursive": true },
    "rear_camera": { "path": "/cameras/rear", "recursive": true },
    "lidar": { "path": "/sensors/lidar", "recursive": false }
  }
}
```

#### 3. Dataset with Metadata

```json
{
  "name": "Annotated Dataset",
  "storage": 1,
  "collection": 2,
  "assets": {
    "path": "/data/annotated",
    "recursive": true
  },
  "excel_metadata_path": "/data/metadata.xlsx"
}
```

## Configuration Parameters

### Required Parameters

| Parameter    | Type    | Description                         | Example            |
| ------------ | ------- | ----------------------------------- | ------------------ |
| `name`       | string  | Display name for the upload         | `"My Dataset"`     |
| `storage`    | integer | Storage backend ID                  | `1`                |
| `collection` | integer | Collection ID defining file specs   | `2`                |
| `assets`     | object  | Path configuration (varies by mode) | See examples below |

### Optional Parameters

| Parameter             | Type     | Default | Description                                                                      |
| --------------------- | -------- | ------- | -------------------------------------------------------------------------------- |
| `description`         | string   | `null`  | Upload description                                                               |
| `project`             | integer  | `null`  | Project ID to associate                                                          |
| `use_single_path`     | boolean  | `false` | Enable individual path mode                                                      |
| `is_recursive`        | boolean  | `false` | Global recursive setting                                                         |
| `excel_metadata_path` | `string` | `null`  | **DEPRECATED** - File path to Excel metadata file (use `excel_metadata` instead) |
| `excel_metadata`      | `object` | `null`  | Base64 encoded Excel metadata (recommended)                                      |

## Excel Metadata Support

The upload plugin provides advanced Excel metadata processing with flexible header support, comprehensive filename matching, and two distinct input methods.

### Input Methods

There are two separate parameters for providing Excel metadata:

#### 1. File Path Method (`excel_metadata_path`) - **DEPRECATED**

:::warning Deprecation Notice
This parameter is **deprecated** and will be removed in a future version.
Please migrate to using the `excel_metadata` parameter with base64 encoding instead.
:::

**Use case:** Traditional file-based uploads where the Excel file exists on the server's file system.

Simple string path to an Excel file:

```json
{
  "excel_metadata_path": "/data/metadata.xlsx"
}
```

**Advantages:**

- Backward compatible with existing implementations
- Simple and straightforward
- Direct file system access

#### 2. Base64 Encoded Method (`excel_metadata`)

**Use case:** Web frontends, APIs, and cloud integrations where files are transmitted as encoded data.

Send Excel file as base64-encoded data with original filename:

```json
{
  "excel_metadata": {
    "data": "UEsDBBQABgAIAAAAIQDd4Z...",
    "filename": "metadata.xlsx"
  }
}
```

**Advantages:**

- No intermediate file storage required
- Perfect for web upload forms
- API-friendly JSON payload
- Automatic temporary file cleanup
- **This is the recommended method going forward**

**Important:** You cannot use both `excel_metadata_path` and `excel_metadata` at the same time

**Migration Example:**

```python
import base64

# Old way (deprecated)
params = {
    "excel_metadata_path": "/data/metadata.xlsx"
}

# New way (recommended)
with open("/data/metadata.xlsx", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")
params = {
    "excel_metadata": {
        "data": encoded,
        "filename": "metadata.xlsx"
    }
}
```

### Excel Format Example

| filename  | category   | quality | notes             |
| --------- | ---------- | ------- | ----------------- |
| sample001 | vehicle    | high    | Clear visibility  |
| sample002 | pedestrian | medium  | Partial occlusion |

### Security Limits

- Max file size: 10MB
- Max rows: 10,000
- Max columns: 50

## File Matching Logic

Files are matched by **stem name** (filename without extension):

- `sample001.jpg` → stem: "sample001"
- `sample001.pcd` → stem: "sample001"
- `sample001.json` → stem: "sample001"

These files form a single dataset named "sample001".

## Troubleshooting Guide

### Common Issues

#### "No Files Found" Error

```bash
# Check path exists and is readable
ls -la /path/to/data
test -r /path/to/data && echo "Readable" || echo "Not readable"

# Verify files exist
find /path/to/data -name "*.jpg" | head -10
```

#### Excel Processing Errors

```bash
# Check file format and size
file /path/to/metadata.xlsx
ls -lh /path/to/metadata.xlsx

# Validate Excel content
python -c "
from openpyxl import load_workbook
wb = load_workbook('/path/to/metadata.xlsx')
print(f'Sheets: {wb.sheetnames}')
print(f'Rows: {wb.active.max_row}')
"
```

#### Upload Failures

```bash
# Test storage connection
synapse storage test --storage-id 1

# Verify collection configuration
synapse collection show --id 2

# Run with debug mode
synapse plugin run upload '{}' --debug
```

## Best Practices

### Directory Organization

- Use clear, descriptive directory names
- Keep reasonable directory sizes (< 10,000 files)
- Use absolute paths for reliability

### Performance Optimization

- Enable recursive only when needed
- Keep Excel files under 5MB
- Organize files in balanced directory structures

### Security Considerations

- Validate all paths before processing
- Use read-only permissions for source data
- Set appropriate Excel size limits

## Advanced Features

### Batch Processing

The plugin automatically optimizes batch sizes based on dataset size:

- Small datasets (< 50 files): batch size 50
- Large datasets: dynamic batch size (10-100)

### Progress Tracking

Real-time progress updates with categories:

- Collection analysis: 2%
- File upload: 38%
- Data unit generation: 60%

### Error Handling

Comprehensive validation at multiple levels:

- Parameter validation (Pydantic)
- Runtime path validation
- File format validation
- Excel security checks

## Environment Variables

Configure Excel processing limits:

```bash
# File size limits
EXCEL_MAX_FILE_SIZE_MB=10
EXCEL_MAX_MEMORY_MB=30

# Content limits
EXCEL_MAX_ROWS=10000
EXCEL_MAX_COLUMNS=50

# String length limits
EXCEL_MAX_FILENAME_LENGTH=255
EXCEL_MAX_METADATA_VALUE_LENGTH=1000
```

## Migration Guide

### Upgrading from Previous Versions

All existing configurations continue to work. New features are additive:

#### Test Current Configuration

```bash
synapse plugin run upload '{}' --debug
```

#### Convert to Explicit Mode

```python
# Add explicit mode setting
config["use_single_path"] = False  # or True for single path mode
```

#### Gradual Migration to Single Path Mode

```python
# Start with subset
test_config = {
    "use_single_path": True,
    "assets": {
        "test_images": {"path": "/existing/path/images", "recursive": True}
    }
}

# Then migrate all assets
production_config = {
    "use_single_path": True,
    "assets": {
        "images": {"path": "/optimized/path1", "recursive": True},
        "annotations": {"path": "/optimized/path2", "recursive": False}
    }
}
```

## Storage Backend Support

The plugin supports multiple storage backends:

- **Local filesystem**: Optimized for high I/O
- **S3/GCS**: Cloud storage with retry logic
- **SFTP**: Connection pooling for remote servers
- **HTTP**: Streaming uploads for large files

## API Reference

### Plugin Class

```python
from synapse import Plugin

plugin = Plugin("upload")
result = plugin.run(config, debug=True)
```

### Result Structure

```python
{
    "status": "success",
    "uploaded_files": 150,
    "data_units_created": 50,
    "errors": [],
    "metadata": {}
}
```

## Support and Resources

- **Documentation**: Full API documentation at [synapse-docs]
- **Issues**: Report bugs at [issue-tracker]
- **Examples**: More examples at [examples-repo]
