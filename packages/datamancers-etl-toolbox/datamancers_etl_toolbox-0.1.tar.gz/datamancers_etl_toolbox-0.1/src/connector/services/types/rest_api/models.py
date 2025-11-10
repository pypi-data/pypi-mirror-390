"""
Data models for the API client library.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class HTTPMethod(str, Enum):
    """HTTP methods supported by the API client."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class RequestConfig:
    """Configuration for individual API requests."""

    method: HTTPMethod
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    data: Optional[Union[Dict[str, Any], str, bytes]] = None
    json: Optional[Dict[str, Any]] = None
    files: Optional[Dict[str, Any]] = None
    timeout: Optional[float] = None
    retries: int = 3
    retry_delay: float = 1.0
    validate_request: bool = True
    validate_response: bool = True


@dataclass
class ResponseConfig:
    """Configuration for API responses."""

    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    data: Optional[Any] = None
    raw_data: Optional[bytes] = None
    is_success: bool = True
    error_message: Optional[str] = None


@dataclass
class SecurityConfig:
    """Security configuration for API authentication."""

    type: str  # apiKey, http, oauth2, openIdConnect
    name: Optional[str] = None
    in_: Optional[str] = None  # query, header, cookie
    scheme: Optional[str] = None
    bearer_format: Optional[str] = None
    value: Optional[str] = None


@dataclass
class ServerConfig:
    """Server configuration."""

    url: str
    description: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationConfig:
    """OpenAPI operation configuration."""

    operation_id: str
    method: HTTPMethod
    path: str
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    security: List[Dict[str, List[str]]] = field(default_factory=list)



