# REST API Client Library

A comprehensive Python library for REST API communication that leverages OpenAPI schemas, supports multiple configuration formats, and uses httpx under the hood.

## Features

- **OpenAPI 3.0 Integration**: Automatic request/response validation using OpenAPI schemas
- **Multiple Configuration Formats**: Support for dict, JSON, and YAML configurations
- **Type Safety**: Full type hints and validation
- **Async Support**: Both synchronous and asynchronous operations
- **HTTP Client**: Built on httpx with retry logic and error handling
- **Security**: Built-in support for various authentication methods
- **Validation**: Request and response validation against OpenAPI schemas
- **Error Handling**: Comprehensive error handling with custom exceptions

## Installation

```bash
pip install httpx pyyaml
```

## Quick Start

### Basic Usage

```python
from etl.external.api_client import APIClient, create_fakturoid_config

# Create configuration
config = create_fakturoid_config(
    api_token="your_api_token",
    account_slug="your_account_slug",
    schema_path="path/to/openapi_schema.json"
)

# Use the client
with APIClient(config) as client:
    # Call operation by ID
    response = client.call_operation(
        operation_id="listInboxFiles",
        path_params={"slug": "your_account_slug"},
        query_params={"page": 1}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Data: {response.data}")
```

### Configuration

#### Dictionary Configuration

```python
from etl.external.api_client import APIClient, load_config

config_dict = {
    "base_url": "https://api.example.com/v1",
    "security": [
        {
            "type": "apiKey",
            "name": "Authorization",
            "in_": "header",
            "value": "Bearer your_token"
        }
    ],
    "schema_path": "path/to/schema.json"
}

config = load_config(config_dict)
client = APIClient(config)
```

#### YAML Configuration

```yaml
# config.yaml
base_url: "https://api.example.com/v1"
api_version: "1.0"
user_agent: "MyApp/1.0.0"
security:
  - type: "apiKey"
    name: "Authorization"
    in_: "header"
    value: "Bearer your_token"
default_headers:
  Content-Type: "application/json"
  Accept: "application/json"
schema_path: "path/to/schema.json"
validate_requests: true
validate_responses: true
```

```python
from etl.external.api_client import APIClient, load_config

config = load_config("config.yaml")
client = APIClient(config)
```

#### JSON Configuration

```json
{
  "base_url": "https://api.example.com/v1",
  "api_version": "1.0",
  "user_agent": "MyApp/1.0.0",
  "security": [
    {
      "type": "apiKey",
      "name": "Authorization",
      "in_": "header",
      "value": "Bearer your_token"
    }
  ],
  "default_headers": {
    "Content-Type": "application/json",
    "Accept": "application/json"
  },
  "schema_path": "path/to/schema.json",
  "validate_requests": true,
  "validate_responses": true
}
```

### Async Usage

```python
import asyncio
from etl.external.api_client import APIClient, create_fakturoid_config

async def main():
    config = create_fakturoid_config(
        api_token="your_api_token",
        account_slug="your_account_slug",
        schema_path="path/to/schema.json"
    )
    
    async with APIClient(config) as client:
        response = await client.acall_operation(
            operation_id="listInboxFiles",
            path_params={"slug": "your_account_slug"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Data: {response.data}")

asyncio.run(main())
```

### Direct HTTP Calls

You can also make direct HTTP calls without OpenAPI schema validation:

```python
with APIClient(config) as client:
    # Direct HTTP calls
    response = client.get("/api/endpoint", params={"param": "value"})
    response = client.post("/api/endpoint", json={"data": "value"})
    response = client.put("/api/endpoint", json={"data": "value"})
    response = client.delete("/api/endpoint")
```

### File Upload

```python
import base64

# Read and encode file
with open("file.pdf", "rb") as f:
    file_content = f.read()
    base64_content = base64.b64encode(file_content).decode('utf-8')
    attachment = f"data:application/pdf;base64,{base64_content}"

# Upload file
response = client.call_operation(
    operation_id="createInboxFile",
    path_params={"slug": "account_slug"},
    body={
        "attachment": attachment,
        "filename": "file.pdf",
        "send_to_ocr": True
    }
)
```

### Error Handling

```python
from etl.external.api_client import APIError, ValidationError, HTTPError

try:
    response = client.call_operation("operation_id", path_params={"id": "123"})
except ValidationError as e:
    print(f"Validation error: {e}")
    print(f"Validation details: {e.validation_errors}")
except HTTPError as e:
    print(f"HTTP error: {e.status_code} - {e.message}")
except APIError as e:
    print(f"API error: {e}")
```

### Operation Discovery

```python
# List all available operations
operations = client.list_operations()
print(f"Available operations: {operations}")

# Get operation information
operation_info = client.get_operation_info("listInboxFiles")
print(f"Operation summary: {operation_info['summary']}")

# Get operations by tag
tagged_operations = client.get_operations_by_tag("Inbox Files")
```

## Configuration Reference

### APIConfig

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `base_url` | str | Base URL for API requests | Required |
| `api_version` | str | API version | None |
| `user_agent` | str | User agent string | "APIClient/1.0.0" |
| `servers` | List[ServerConfig] | Server configurations | [] |
| `security` | List[SecurityConfig] | Security configurations | [] |
| `default_timeout` | float | Default request timeout | 30.0 |
| `default_retries` | int | Default number of retries | 3 |
| `default_retry_delay` | float | Default retry delay | 1.0 |
| `validate_requests` | bool | Validate requests against schema | True |
| `validate_responses` | bool | Validate responses against schema | True |
| `strict_validation` | bool | Use strict validation | False |
| `follow_redirects` | bool | Follow HTTP redirects | True |
| `max_redirects` | int | Maximum redirects to follow | 10 |
| `default_headers` | Dict[str, str] | Default request headers | {} |
| `openapi_schema` | Dict[str, Any] | OpenAPI schema dictionary | None |
| `schema_path` | str | Path to OpenAPI schema file | None |

### SecurityConfig

| Field | Type | Description |
|-------|------|-------------|
| `type` | str | Security type (apiKey, http, oauth2, openIdConnect) |
| `name` | str | Parameter name (for apiKey) |
| `in_` | str | Parameter location (query, header, cookie) |
| `scheme` | str | HTTP scheme (for http) |
| `bearer_format` | str | Bearer format (for http) |
| `value` | str | Security value |

## Examples

See the `examples/` directory for complete examples:

- `fakturoid_example.py` - Complete Fakturoid API example
- `config_examples.yaml` - YAML configuration example
- `config_examples.json` - JSON configuration example

## Dependencies

- `httpx` - HTTP client library
- `pyyaml` - YAML parsing (optional, for YAML configs)

## License

This library is part of the ETL project and follows the same license terms.



