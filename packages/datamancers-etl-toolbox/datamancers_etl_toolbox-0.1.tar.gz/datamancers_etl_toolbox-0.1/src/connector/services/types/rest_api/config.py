"""
Configuration management for the API client library.
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from .exceptions import ConfigurationError
from .models import SecurityConfig, ServerConfig


@dataclass
class APIConfig:
    """Main configuration class for the API client."""

    # Basic configuration
    base_url: str
    api_version: Optional[str] = None
    user_agent: str = "APIClient/1.0.0"

    # Server configuration
    servers: List[ServerConfig] = field(default_factory=list)

    # Security configuration
    security: List[SecurityConfig] = field(default_factory=list)

    # Default request configuration
    default_timeout: float = 30.0
    default_retries: int = 3
    default_retry_delay: float = 1.0

    # Validation settings
    validate_requests: bool = True
    validate_responses: bool = True
    strict_validation: bool = False

    # HTTP settings
    follow_redirects: bool = True
    max_redirects: int = 10

    # Headers
    default_headers: Dict[str, str] = field(default_factory=dict)

    # OpenAPI schema
    openapi_schema: Optional[Dict[str, Any]] = None
    schema_path: Optional[str] = None

    def __post_init__(self):
        """Post-initialization validation."""
        if not self.base_url:
            raise ConfigurationError("base_url is required")

        # Set default server if none provided
        if not self.servers:
            self.servers = [ServerConfig(url=self.base_url)]

        # Add default headers
        if "User-Agent" not in self.default_headers:
            self.default_headers["User-Agent"] = self.user_agent


def load_config(
    config_source: Union[str, Path, Dict[str, Any]], config_type: Optional[str] = None
) -> APIConfig:
    """
    Load configuration from various sources.

    Args:
        config_source: Configuration source (file path, dict, or JSON string)
        config_type: Type of configuration ('yaml', 'json', 'dict'). Auto-detected if None.

    Returns:
        APIConfig: Loaded configuration object

    Raises:
        ConfigurationError: If configuration loading fails
    """
    if isinstance(config_source, dict):
        return _load_from_dict(config_source)

    if isinstance(config_source, (str, Path)):
        path = Path(config_source)

        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {path}")

        # Auto-detect file type
        if config_type is None:
            suffix = path.suffix.lower()
            if suffix in [".yaml", ".yml"]:
                config_type = "yaml"
            elif suffix in [".json"]:
                config_type = "json"
            else:
                raise ConfigurationError(f"Unsupported file type: {suffix}")

        # Load based on type
        if config_type == "yaml":
            return _load_from_yaml(path)
        elif config_type == "json":
            return _load_from_json(path)
        else:
            raise ConfigurationError(f"Unsupported config type: {config_type}")

    raise ConfigurationError(f"Unsupported config source type: {type(config_source)}")


def _load_from_dict(config_dict: Dict[str, Any]) -> APIConfig:
    """Load configuration from a dictionary."""
    try:
        # Convert servers
        servers = []
        for server_data in config_dict.get("servers", []):
            servers.append(ServerConfig(**server_data))

        # Convert security
        security = []
        for security_data in config_dict.get("security", []):
            security.append(SecurityConfig(**security_data))

        # Create config object
        config = APIConfig(
            base_url=config_dict["base_url"],
            api_version=config_dict.get("api_version"),
            user_agent=config_dict.get("user_agent", "APIClient/1.0.0"),
            servers=servers,
            security=security,
            default_timeout=config_dict.get("default_timeout", 30.0),
            default_retries=config_dict.get("default_retries", 3),
            default_retry_delay=config_dict.get("default_retry_delay", 1.0),
            validate_requests=config_dict.get("validate_requests", True),
            validate_responses=config_dict.get("validate_responses", True),
            strict_validation=config_dict.get("strict_validation", False),
            follow_redirects=config_dict.get("follow_redirects", True),
            max_redirects=config_dict.get("max_redirects", 10),
            default_headers=config_dict.get("default_headers", {}),
            openapi_schema=config_dict.get("openapi_schema"),
            schema_path=config_dict.get("schema_path"),
        )

        return config

    except KeyError as e:
        raise ConfigurationError(f"Missing required configuration key: {e}")
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration: {e}")


def _load_from_yaml(path: Path) -> APIConfig:
    """Load configuration from YAML file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
        return _load_from_dict(config_dict)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML configuration: {e}")
    except Exception as e:
        raise ConfigurationError(f"Failed to load YAML configuration: {e}")


def _load_from_json(path: Path) -> APIConfig:
    """Load configuration from JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
        return _load_from_dict(config_dict)
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON configuration: {e}")
    except Exception as e:
        raise ConfigurationError(f"Failed to load JSON configuration: {e}")


def create_fakturoid_config(
    api_token: str, account_slug: str, schema_path: Optional[str] = None
) -> APIConfig:
    """
    Create a pre-configured APIConfig for Fakturoid API.

    Args:
        api_token: Fakturoid API token
        account_slug: Fakturoid account slug
        schema_path: Path to OpenAPI schema file

    Returns:
        APIConfig: Pre-configured for Fakturoid API
    """
    return APIConfig(
        base_url="https://app.fakturoid.cz/api/v3",
        api_version="3.0",
        user_agent="FakturoidAPIClient/1.0.0",
        servers=[
            ServerConfig(
                url="https://app.fakturoid.cz/api/v3", description="Fakturoid API v3"
            )
        ],
        security=[
            SecurityConfig(
                type="apiKey",
                name="Authorization",
                in_="header",
                value=f"Token token={api_token}",
            )
        ],
        default_headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        schema_path=schema_path,
        validate_requests=True,
        validate_responses=True,
    )



