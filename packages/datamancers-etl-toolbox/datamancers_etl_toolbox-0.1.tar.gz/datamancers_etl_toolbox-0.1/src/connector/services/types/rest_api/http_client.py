"""
HTTP client wrapper using httpx.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from httpx import Response, Request, HTTPError as HttpxHTTPError

from .exceptions import HTTPError, APIError
from .models import RequestConfig, ResponseConfig, HTTPMethod


class HTTPClient:
    """HTTP client wrapper using httpx with retry and error handling."""

    def __init__(
        self,
        base_url: str,
        default_headers: Optional[Dict[str, str]] = None,
        default_timeout: float = 30.0,
        default_retries: int = 3,
        default_retry_delay: float = 1.0,
        follow_redirects: bool = True,
        max_redirects: int = 10,
    ):
        """
        Initialize HTTP client.

        Args:
            base_url: Base URL for all requests
            default_headers: Default headers for all requests
            default_timeout: Default timeout in seconds
            default_retries: Default number of retries
            default_retry_delay: Default delay between retries in seconds
            follow_redirects: Whether to follow redirects
            max_redirects: Maximum number of redirects to follow
        """
        self.base_url = base_url.rstrip("/")
        self.default_headers = default_headers or {}
        self.default_timeout = default_timeout
        self.default_retries = default_retries
        self.default_retry_delay = default_retry_delay
        self.follow_redirects = follow_redirects
        self.max_redirects = max_redirects

        # Create httpx client
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self.default_headers,
            timeout=default_timeout,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
        )

        # Async client (created on demand)
        self._async_client: Optional[httpx.AsyncClient] = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()
        if self._async_client:
            asyncio.run(self._async_client.aclose())

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()

    async def aclose(self):
        """Close the async HTTP client."""
        if self._async_client:
            await self._async_client.aclose()

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.default_headers,
                timeout=self.default_timeout,
                follow_redirects=self.follow_redirects,
                max_redirects=self.max_redirects,
            )
        return self._async_client

    def request(
        self,
        method: Union[str, HTTPMethod],
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
    ) -> ResponseConfig:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            params: Query parameters
            data: Request data
            json: JSON data
            files: File uploads
            timeout: Request timeout
            retries: Number of retries
            retry_delay: Delay between retries

        Returns:
            ResponseConfig: Response configuration object
        """
        if isinstance(method, HTTPMethod):
            method = method.value

        retries = retries or self.default_retries
        retry_delay = retry_delay or self.default_retry_delay
        timeout = timeout or self.default_timeout

        last_exception = None

        for attempt in range(retries + 1):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    data=data,
                    json=json,
                    files=files,
                    timeout=timeout,
                )

                return self._process_response(response)

            except HttpxHTTPError as e:
                last_exception = e

                # Don't retry on client errors (4xx)
                if hasattr(e, "response") and e.response.status_code < 500:
                    raise HTTPError(
                        f"HTTP error: {e}",
                        status_code=getattr(e.response, "status_code", None),
                        response_data=getattr(e.response, "json", lambda: None)(),
                    )

                # Retry on server errors (5xx) or network errors
                if attempt < retries:
                    time.sleep(retry_delay * (2**attempt))  # Exponential backoff
                    continue
                else:
                    raise HTTPError(f"HTTP error after {retries} retries: {e}")

            except Exception as e:
                last_exception = e
                if attempt < retries:
                    time.sleep(retry_delay * (2**attempt))
                    continue
                else:
                    raise APIError(f"Request failed after {retries} retries: {e}")

        # This should never be reached, but just in case
        raise APIError(f"Request failed: {last_exception}")

    async def arequest(
        self,
        method: Union[str, HTTPMethod],
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
    ) -> ResponseConfig:
        """
        Make async HTTP request with retry logic.

        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            params: Query parameters
            data: Request data
            json: JSON data
            files: File uploads
            timeout: Request timeout
            retries: Number of retries
            retry_delay: Delay between retries

        Returns:
            ResponseConfig: Response configuration object
        """
        if isinstance(method, HTTPMethod):
            method = method.value

        retries = retries or self.default_retries
        retry_delay = retry_delay or self.default_retry_delay
        timeout = timeout or self.default_timeout

        client = self._get_async_client()
        last_exception = None

        for attempt in range(retries + 1):
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    data=data,
                    json=json,
                    files=files,
                    timeout=timeout,
                )

                return self._process_response(response)

            except HttpxHTTPError as e:
                last_exception = e

                # Don't retry on client errors (4xx)
                if hasattr(e, "response") and e.response.status_code < 500:
                    raise HTTPError(
                        f"HTTP error: {e}",
                        status_code=getattr(e.response, "status_code", None),
                        response_data=getattr(e.response, "json", lambda: None)(),
                    )

                # Retry on server errors (5xx) or network errors
                if attempt < retries:
                    await asyncio.sleep(retry_delay * (2**attempt))
                    continue
                else:
                    raise HTTPError(f"HTTP error after {retries} retries: {e}")

            except Exception as e:
                last_exception = e
                if attempt < retries:
                    await asyncio.sleep(retry_delay * (2**attempt))
                    continue
                else:
                    raise APIError(f"Request failed after {retries} retries: {e}")

        # This should never be reached, but just in case
        raise APIError(f"Request failed: {last_exception}")

    def _process_response(self, response: Response) -> ResponseConfig:
        """
        Process httpx response into ResponseConfig.

        Args:
            response: httpx Response object

        Returns:
            ResponseConfig: Processed response configuration
        """
        # Try to parse JSON response
        try:
            data = response.json()
        except Exception:
            data = response.text

        # Determine if response is successful
        is_success = 200 <= response.status_code < 300

        # Get error message if not successful
        error_message = None
        if not is_success:
            if isinstance(data, dict):
                error_message = (
                    data.get("message") or data.get("error") or data.get("detail")
                )
            elif isinstance(data, str):
                error_message = data

        return ResponseConfig(
            status_code=response.status_code,
            headers=dict(response.headers),
            data=data,
            raw_data=response.content,
            is_success=is_success,
            error_message=error_message,
        )

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make GET request."""
        return self.request("GET", url, params=params, headers=headers, **kwargs)

    def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make POST request."""
        return self.request(
            "POST", url, data=data, json=json, headers=headers, **kwargs
        )

    def put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make PUT request."""
        return self.request("PUT", url, data=data, json=json, headers=headers, **kwargs)

    def delete(
        self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> ResponseConfig:
        """Make DELETE request."""
        return self.request("DELETE", url, headers=headers, **kwargs)

    def patch(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make PATCH request."""
        return self.request(
            "PATCH", url, data=data, json=json, headers=headers, **kwargs
        )

    # Async versions
    async def aget(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make async GET request."""
        return await self.arequest("GET", url, params=params, headers=headers, **kwargs)

    async def apost(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make async POST request."""
        return await self.arequest(
            "POST", url, data=data, json=json, headers=headers, **kwargs
        )

    async def aput(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make async PUT request."""
        return await self.arequest(
            "PUT", url, data=data, json=json, headers=headers, **kwargs
        )

    async def adelete(
        self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> ResponseConfig:
        """Make async DELETE request."""
        return await self.arequest("DELETE", url, headers=headers, **kwargs)

    async def apatch(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make async PATCH request."""
        return await self.arequest(
            "PATCH", url, data=data, json=json, headers=headers, **kwargs
        )



