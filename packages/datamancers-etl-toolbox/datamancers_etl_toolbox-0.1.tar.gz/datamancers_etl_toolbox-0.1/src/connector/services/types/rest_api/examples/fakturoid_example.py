"""
Example usage of the API client with Fakturoid API.
"""

import asyncio
import base64
from pathlib import Path

from ..client import APIClient
from ..config import create_fakturoid_config, load_config


def sync_example():
    """Synchronous example using Fakturoid API."""
    print("=== Synchronous Fakturoid API Example ===")

    # Create configuration
    config = create_fakturoid_config(
        api_token="your_api_token_here",
        account_slug="your_account_slug",
        schema_path="../../openapi_schema/fakturoid.json",
    )

    # Create API client
    with APIClient(config) as client:
        try:
            # List available operations
            operations = client.list_operations()
            print(f"Available operations: {operations}")

            # Get operation info
            operation_info = client.get_operation_info("listInboxFiles")
            if operation_info:
                print(f"Operation info: {operation_info['summary']}")

            # Call operation using OpenAPI schema
            response = client.call_operation(
                operation_id="listInboxFiles",
                path_params={"slug": "your_account_slug"},
                query_params={"page": 1},
            )

            print(f"Status: {response.status_code}")
            print(f"Success: {response.is_success}")
            if response.data:
                print(f"Data: {response.data}")

            # Direct API call (without schema validation)
            response = client.get(
                path="/accounts/your_account_slug/inbox_files.json", params={"page": 1}
            )

            print(f"Direct call status: {response.status_code}")

        except Exception as e:
            print(f"Error: {e}")


async def async_example():
    """Asynchronous example using Fakturoid API."""
    print("\n=== Asynchronous Fakturoid API Example ===")

    # Create configuration
    config = create_fakturoid_config(
        api_token="your_api_token_here",
        account_slug="your_account_slug",
        schema_path="../../openapi_schema/fakturoid.json",
    )

    # Create API client
    async with APIClient(config) as client:
        try:
            # List available operations
            operations = client.list_operations()
            print(f"Available operations: {operations}")

            # Call operation using OpenAPI schema
            response = await client.acall_operation(
                operation_id="listInboxFiles",
                path_params={"slug": "your_account_slug"},
                query_params={"page": 1},
            )

            print(f"Status: {response.status_code}")
            print(f"Success: {response.is_success}")
            if response.data:
                print(f"Data: {response.data}")

            # Direct API call
            response = await client.aget(
                path="/accounts/your_account_slug/inbox_files.json", params={"page": 1}
            )

            print(f"Direct call status: {response.status_code}")

        except Exception as e:
            print(f"Error: {e}")


def config_examples():
    """Examples of different configuration formats."""
    print("\n=== Configuration Examples ===")

    # Dictionary configuration
    dict_config = {
        "base_url": "https://app.fakturoid.cz/api/v3",
        "api_version": "3.0",
        "user_agent": "MyApp/1.0.0",
        "security": [
            {
                "type": "apiKey",
                "name": "Authorization",
                "in_": "header",
                "value": "Token token=your_api_token_here",
            }
        ],
        "default_headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        "schema_path": "../../openapi_schema/fakturoid.json",
        "validate_requests": True,
        "validate_responses": True,
    }

    # Load from dictionary
    config = load_config(dict_config)
    print(f"Loaded config from dict: {config.base_url}")

    # YAML configuration example
    yaml_config = """
base_url: https://app.fakturoid.cz/api/v3
api_version: "3.0"
user_agent: "MyApp/1.0.0"
security:
  - type: apiKey
    name: Authorization
    in_: header
    value: "Token token=your_api_token_here"
default_headers:
  Content-Type: application/json
  Accept: application/json
schema_path: "../../openapi_schema/fakturoid.json"
validate_requests: true
validate_responses: true
default_timeout: 30.0
default_retries: 3
"""

    # Save YAML config to file
    yaml_file = Path("fakturoid_config.yaml")
    yaml_file.write_text(yaml_config)

    # Load from YAML file
    config = load_config(yaml_file)
    print(f"Loaded config from YAML: {config.base_url}")

    # Clean up
    yaml_file.unlink()


def file_upload_example():
    """Example of file upload to Fakturoid."""
    print("\n=== File Upload Example ===")

    config = create_fakturoid_config(
        api_token="your_api_token_here",
        account_slug="your_account_slug",
        schema_path="../../openapi_schema/fakturoid.json",
    )

    with APIClient(config) as client:
        try:
            # Read file and encode as base64
            file_path = Path("example_invoice.pdf")
            if file_path.exists():
                with open(file_path, "rb") as f:
                    file_content = f.read()

                # Encode as base64 with MIME type
                base64_content = base64.b64encode(file_content).decode("utf-8")
                attachment = f"data:application/pdf;base64,{base64_content}"

                # Upload file
                response = client.call_operation(
                    operation_id="createInboxFile",
                    path_params={"slug": "your_account_slug"},
                    body={
                        "attachment": attachment,
                        "filename": "example_invoice.pdf",
                        "send_to_ocr": True,
                    },
                )

                print(f"Upload status: {response.status_code}")
                if response.data:
                    print(f"Uploaded file ID: {response.data.get('id')}")
            else:
                print("Example file not found, skipping upload")

        except Exception as e:
            print(f"Upload error: {e}")


def error_handling_example():
    """Example of error handling."""
    print("\n=== Error Handling Example ===")

    config = create_fakturoid_config(
        api_token="invalid_token",
        account_slug="invalid_slug",
        schema_path="../../openapi_schema/fakturoid.json",
    )

    with APIClient(config) as client:
        try:
            response = client.call_operation(
                operation_id="listInboxFiles", path_params={"slug": "invalid_slug"}
            )

            if not response.is_success:
                print(f"API Error: {response.status_code} - {response.error_message}")

        except Exception as e:
            print(f"Client Error: {e}")


if __name__ == "__main__":
    # Run synchronous example
    sync_example()

    # Run asynchronous example
    asyncio.run(async_example())

    # Run configuration examples
    config_examples()

    # Run file upload example
    file_upload_example()

    # Run error handling example
    error_handling_example()
