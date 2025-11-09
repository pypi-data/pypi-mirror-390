"""HTTP client wrapper for Archive-It API using httpx with standardized error handling."""

import logging

import httpx

logger = logging.getLogger(__name__)


class HTTPXClient:
    """Wrapper around httpx.Client with standardized error handling for Archive-It API."""

    def __init__(
        self,
        base_url: str,
        auth: tuple[str, str],
        follow_redirects: bool = True,
        timeout: float | None = None,
    ) -> None:
        """Initialize the HTTP client.

        Args:
            base_url: Base URL for API requests
            auth: Tuple of (username, password) for authentication
            follow_redirects: Whether to follow redirects
            timeout: Request timeout in seconds
        """
        self.client = httpx.Client(
            base_url=base_url,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
        )

    def request(
        self, method: str, endpoint: str, **kwargs: dict | bool
    ) -> httpx.Response:
        """Make an HTTP request with standardized error handling.

        Args:
            method: HTTP method (get, post, patch, delete, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to httpx

        Returns:
            httpx.Response: The HTTP response

        Raises:
            httpx.HTTPStatusError: If the request fails
            httpx.TimeoutException: If the request times out
            Exception: For other errors
        """
        # Ensure method is valid
        if method.lower() not in {
            "get",
            "post",
            "patch",
            "delete",
            "put",
            "head",
            "options",
        }:
            msg = f"Invalid HTTP method: {method}"
            raise ValueError(msg)

        try:
            response = getattr(self.client, method.lower())(endpoint, **kwargs)
            response.raise_for_status()
            # Note: Handle HTTP errors (response.raise_for_status()) application side
            return response
        except httpx.TimeoutException as e:
            logger.error(f"Timeout for {method.upper()} {endpoint}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during {method.upper()} {endpoint}: {e}")
            raise

    def get(self, endpoint: str, **kwargs: dict) -> httpx.Response:
        """Make a GET request."""
        return self.request("get", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: dict) -> httpx.Response:
        """Make a POST request."""
        return self.request("post", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs: dict) -> httpx.Response:
        """Make a PATCH request."""
        return self.request("patch", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: dict) -> httpx.Response:
        """Make a DELETE request."""
        return self.request("delete", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: dict) -> httpx.Response:
        """Make a PUT request."""
        return self.request("put", endpoint, **kwargs)

    def head(self, endpoint: str, **kwargs: dict) -> httpx.Response:
        """Make a HEAD request."""
        return self.request("head", endpoint, **kwargs)

    def options(self, endpoint: str, **kwargs: dict) -> httpx.Response:
        """Make an OPTIONS request."""
        return self.request("options", endpoint, **kwargs)

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()
