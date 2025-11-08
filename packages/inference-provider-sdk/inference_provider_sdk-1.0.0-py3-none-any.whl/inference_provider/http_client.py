"""
HTTP client with retry logic and error handling
"""

import asyncio
import random
import time
from typing import Any, Dict, Optional

import httpx

from inference_provider.auth import create_auth_headers
from inference_provider.errors import APIError, NetworkError, create_error_from_response


class RetryConfig:
    """Retry configuration"""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay_ms: int = 1000,
        max_delay_ms: int = 10000,
        backoff_multiplier: float = 2.0,
    ):
        self.max_retries = max_retries
        self.initial_delay_ms = initial_delay_ms
        self.max_delay_ms = max_delay_ms
        self.backoff_multiplier = backoff_multiplier


def calculate_retry_delay(attempt: int, config: RetryConfig) -> float:
    """
    Calculate retry delay with exponential backoff and jitter

    Args:
        attempt: Retry attempt number (0-indexed)
        config: Retry configuration

    Returns:
        Delay in seconds
    """
    base_delay_ms = config.initial_delay_ms * (config.backoff_multiplier**attempt)
    delay_ms = min(base_delay_ms, config.max_delay_ms)

    # Add jitter (±25%)
    jitter = delay_ms * 0.25 * (random.random() * 2 - 1)
    final_delay_ms = delay_ms + jitter

    return final_delay_ms / 1000  # Convert to seconds


def is_retryable_error(response: Optional[httpx.Response]) -> bool:
    """
    Determine if error is retryable

    Args:
        response: HTTP response or None for network errors

    Returns:
        True if retryable
    """
    if response is None:
        # Network error - retryable
        return True

    status_code = response.status_code
    # Retry on rate limit, server errors, and gateway errors
    return status_code in (429, 500, 502, 503, 504)


class HttpClient:
    """Sync HTTP client for making API requests"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        api_secret: str,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        debug: bool = False,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.debug = debug
        self.retry_config = RetryConfig(max_retries=max_retries or 3)

        # Create headers
        headers = {
            "Content-Type": "application/json",
            **create_auth_headers(api_key, api_secret),
        }

        # Create client
        self.client = httpx.Client(
            base_url=base_url,
            headers=headers,
            timeout=timeout or 60.0,
        )

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client"""
        self.client.close()

    def _request_with_retry(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        attempt: int = 0,
    ) -> httpx.Response:
        """
        Make HTTP request with automatic retry logic

        Args:
            method: HTTP method
            url: URL path
            data: Request data
            attempt: Current attempt number

        Returns:
            HTTP response

        Raises:
            InferenceProviderError: On error
        """
        try:
            if self.debug:
                print(f"[HTTP Request] {method} {url}")
                if data:
                    print(f"[HTTP Request Data] {data}")

            response = self.client.request(method, url, json=data)

            if self.debug:
                print(f"[HTTP Response] {response.status_code}")
                print(f"[HTTP Response Data] {response.text[:500]}")

            # Check for errors
            if response.status_code >= 400:
                # Try to retry if retryable
                if attempt < self.retry_config.max_retries and is_retryable_error(response):
                    delay = calculate_retry_delay(attempt, self.retry_config)

                    if self.debug:
                        print(
                            f"[HTTP Retry] Attempt {attempt + 1}/"
                            f"{self.retry_config.max_retries}, waiting {delay:.2f}s"
                        )

                    time.sleep(delay)
                    return self._request_with_retry(method, url, data, attempt + 1)

                # No more retries, raise error
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {"error": response.text or "Unknown error"}

                raise create_error_from_response(response.status_code, error_data)

            return response

        except httpx.RequestError as e:
            # Network error
            if attempt < self.retry_config.max_retries:
                delay = calculate_retry_delay(attempt, self.retry_config)

                if self.debug:
                    print(
                        f"[HTTP Retry] Network error, attempt {attempt + 1}/"
                        f"{self.retry_config.max_retries}, waiting {delay:.2f}s"
                    )

                time.sleep(delay)
                return self._request_with_retry(method, url, data, attempt + 1)

            raise NetworkError(str(e), e)

    def get(self, url: str) -> Any:
        """Make GET request"""
        response = self._request_with_retry("GET", url)
        return response.json()

    def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make POST request"""
        response = self._request_with_retry("POST", url, data)
        return response.json()

    def put(self, url: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make PUT request"""
        response = self._request_with_retry("PUT", url, data)
        return response.json()

    def delete(self, url: str) -> Any:
        """Make DELETE request"""
        response = self._request_with_retry("DELETE", url)
        return response.json()

    def patch(self, url: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make PATCH request"""
        response = self._request_with_retry("PATCH", url, data)
        return response.json()


class AsyncHttpClient:
    """Async HTTP client for making API requests"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        api_secret: str,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        debug: bool = False,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.debug = debug
        self.retry_config = RetryConfig(max_retries=max_retries or 3)

        # Create headers
        headers = {
            "Content-Type": "application/json",
            **create_auth_headers(api_key, api_secret),
        }

        # Create client
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout or 60.0,
        )

    async def __aenter__(self) -> "AsyncHttpClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client"""
        await self.client.aclose()

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        attempt: int = 0,
    ) -> httpx.Response:
        """
        Make HTTP request with automatic retry logic

        Args:
            method: HTTP method
            url: URL path
            data: Request data
            attempt: Current attempt number

        Returns:
            HTTP response

        Raises:
            InferenceProviderError: On error
        """
        try:
            if self.debug:
                print(f"[HTTP Request] {method} {url}")
                if data:
                    print(f"[HTTP Request Data] {data}")

            response = await self.client.request(method, url, json=data)

            if self.debug:
                print(f"[HTTP Response] {response.status_code}")
                print(f"[HTTP Response Data] {response.text[:500]}")

            # Check for errors
            if response.status_code >= 400:
                # Try to retry if retryable
                if attempt < self.retry_config.max_retries and is_retryable_error(response):
                    delay = calculate_retry_delay(attempt, self.retry_config)

                    if self.debug:
                        print(
                            f"[HTTP Retry] Attempt {attempt + 1}/"
                            f"{self.retry_config.max_retries}, waiting {delay:.2f}s"
                        )

                    await asyncio.sleep(delay)
                    return await self._request_with_retry(method, url, data, attempt + 1)

                # No more retries, raise error
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {"error": response.text or "Unknown error"}

                raise create_error_from_response(response.status_code, error_data)

            return response

        except httpx.RequestError as e:
            # Network error
            if attempt < self.retry_config.max_retries:
                delay = calculate_retry_delay(attempt, self.retry_config)

                if self.debug:
                    print(
                        f"[HTTP Retry] Network error, attempt {attempt + 1}/"
                        f"{self.retry_config.max_retries}, waiting {delay:.2f}s"
                    )

                await asyncio.sleep(delay)
                return await self._request_with_retry(method, url, data, attempt + 1)

            raise NetworkError(str(e), e)

    async def get(self, url: str) -> Any:
        """Make GET request"""
        response = await self._request_with_retry("GET", url)
        return response.json()

    async def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make POST request"""
        response = await self._request_with_retry("POST", url, data)
        return response.json()

    async def put(self, url: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make PUT request"""
        response = await self._request_with_retry("PUT", url, data)
        return response.json()

    async def delete(self, url: str) -> Any:
        """Make DELETE request"""
        response = await self._request_with_retry("DELETE", url)
        return response.json()

    async def patch(self, url: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make PATCH request"""
        response = await self._request_with_retry("PATCH", url, data)
        return response.json()
