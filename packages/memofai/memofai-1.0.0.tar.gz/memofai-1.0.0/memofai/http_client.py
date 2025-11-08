"""
HTTP client for the memofai SDK.

This module provides the HTTP client with retry logic, error handling,
and request/response interceptors.
"""

import os
import platform
import time
from typing import Any, Dict, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .types import (
    ClientConfig,
    ApiResponse,
    Headers,
    HttpMethod,
    ENVIRONMENTS,
    MoaErrorResponse,
)
from .exceptions import (
    ApiError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ServiceUnavailableError,
    RequestLimitError,
    NetworkError,
)
from .version import SDK_VERSION


class RequestConfig:
    """Configuration for a single request."""

    def __init__(
        self,
        path: str,
        method: HttpMethod,
        query_params: Optional[Dict[str, Union[str, int, bool]]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Headers] = None,
    ):
        self.path = path
        self.method = method
        self.query_params = query_params
        self.body = body
        self.headers = headers


class HttpClient:
    """HTTP client with retry logic and error handling."""

    def __init__(self, config: ClientConfig):
        self.config = config
        environment = config.environment

        # Validate environment
        if environment not in ENVIRONMENTS:
            valid_envs = ", ".join(ENVIRONMENTS.keys())
            raise ValueError(
                f'Invalid environment: "{environment}". Valid options are: {valid_envs}'
            )

        self.base_url = ENVIRONMENTS[environment].base_url
        self.user_agent = self._generate_user_agent()

        # Create session with retry strategy
        self.session = requests.Session()

        # Configure retry strategy for 5xx errors
        retry_strategy = Retry(
            total=0,  # We'll handle retries manually for more control
            status_forcelist=[500, 502, 503, 504],
            backoff_factor=1,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update(
            {
                "Authorization": f"Token {config.api_token}",
                "Content-Type": "application/json",
                "User-Agent": self.user_agent,
            }
        )

    def _generate_user_agent(self) -> str:
        """Generate User-Agent string."""
        sdk_info = f"memofai-python/{SDK_VERSION}"
        python_version = platform.python_version()
        system_info = f"{platform.system()}/{platform.release()}"
        return f"{sdk_info} (Python/{python_version}; {system_info})"

    def _should_retry(self, status_code: int) -> bool:
        """Determine if a request should be retried based on status code."""
        return 500 <= status_code < 600

    def _delay(self, delay_ms: int) -> None:
        """Delay execution for the specified milliseconds."""
        time.sleep(delay_ms / 1000.0)

    def _transform_response(self, data: Any) -> Any:
        """Transform response data, unwrapping if needed."""
        if isinstance(data, dict):
            # If the response has a 'data' field with 'success' flag, unwrap it
            if "success" in data and "data" in data:
                return data["data"]
        return data

    def _parse_error_response(self, response: requests.Response) -> MoaErrorResponse:
        """Parse error response into MoaErrorResponse."""
        try:
            data = response.json()
        except Exception:
            data = {}

        error_response = MoaErrorResponse(
            detail=data.get("detail"),
            error_type=data.get("error_type"),
            resource_type=data.get("resource_type"),
            limit=data.get("limit"),
            current_usage=data.get("current_usage"),
        )

        # Add any extra fields
        for key, value in data.items():
            if key not in ["detail", "error_type", "resource_type", "limit", "current_usage"]:
                error_response.extra[key] = value

        return error_response

    def _create_specific_error(
        self,
        message: str,
        status: int,
        status_text: str,
        response: requests.Response,
    ) -> Exception:
        """Create a specific error based on status code."""
        error_response = self._parse_error_response(response)

        # Override message if detail is available
        if error_response.detail:
            message = error_response.detail

        if status == 400:
            return ValidationError(status, status_text, error_response)
        elif status == 401:
            return AuthenticationError(status, status_text, error_response)
        elif status == 403:
            return AuthorizationError(status, status_text, error_response)
        elif status == 404:
            return NotFoundError(status, status_text, error_response)
        elif status == 429:
            return RequestLimitError(status, status_text, error_response)
        elif status in [503, 504]:
            return ServiceUnavailableError(status, status_text, error_response)
        else:
            return ApiError(message, status, status_text, error_response)

    def request(self, config: RequestConfig) -> ApiResponse:
        """
        Execute an HTTP request with retry logic.

        Args:
            config: Request configuration

        Returns:
            ApiResponse with the response data

        Raises:
            ApiError: When the request fails
            NetworkError: When a network error occurs
        """
        url = f"{self.base_url}{config.path}"

        # Prepare request kwargs
        kwargs: Dict[str, Any] = {
            "method": config.method,
            "url": url,
            "timeout": self.config.timeout / 1000.0,  # Convert ms to seconds
        }

        if config.query_params:
            kwargs["params"] = config.query_params

        if config.body:
            kwargs["json"] = config.body

        if config.headers:
            kwargs["headers"] = {**self.session.headers, **config.headers}

        # Debug logging
        if os.environ.get("MOA_DEBUG") == "true":
            print(f"[API] {config.method} {url}")

        # Retry logic
        last_exception: Optional[Exception] = None
        retry_count = 0

        while retry_count <= self.config.retries:
            try:
                response = self.session.request(**kwargs)

                # Debug logging
                if os.environ.get("MOA_DEBUG") == "true":
                    print(f"[API] Response {response.status_code} for {url}")

                # Check if request was successful
                if response.ok:
                    data = response.json() if response.content else None
                    transformed_data = self._transform_response(data)

                    return ApiResponse(
                        data=transformed_data,
                        status=response.status_code,
                        status_text=response.reason,
                        headers=dict(response.headers),
                    )
                else:
                    # Handle error response
                    status_text = response.reason or "Unknown Error"
                    message = response.text or "Request failed"

                    # Check if we should retry
                    if (
                        self._should_retry(response.status_code)
                        and retry_count < self.config.retries
                    ):
                        retry_count += 1
                        if os.environ.get("MOA_DEBUG") == "true":
                            print(f"[API] Retrying request ({retry_count}/{self.config.retries})")
                        self._delay(self.config.retry_delay)
                        continue

                    # Create and raise specific error
                    error = self._create_specific_error(
                        message, response.status_code, status_text, response
                    )
                    raise error

            except requests.exceptions.RequestException as e:
                last_exception = e

                # Check if we should retry
                if retry_count < self.config.retries:
                    retry_count += 1
                    if os.environ.get("MOA_DEBUG") == "true":
                        print(f"[API] Retrying request ({retry_count}/{self.config.retries})")
                    self._delay(self.config.retry_delay)
                    continue

                # Raise network error
                raise NetworkError(f"Network error: {str(e)}", e)

        # If we get here, all retries failed
        if last_exception:
            raise NetworkError(
                f"Request failed after {self.config.retries} retries", last_exception
            )

        raise NetworkError("Request failed", Exception("Unknown error"))
