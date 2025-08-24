"""Custom exceptions for the client."""

from typing import Any, Dict, Optional

HTTP401 = 401
HTTP400 = 400
HTTP429 = 429
HTTP500 = 500


class CurrentsAPIError(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize exception.

        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Response data if any
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class CurrentsAuthenticationError(CurrentsAPIError):
    """Authentication failed."""

    def __init__(self, message: str = 'Invalid API key or authentication failed') -> None:
        """Initialize authentication error.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=HTTP401)


class CurrentsRateLimitError(CurrentsAPIError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str = 'API rate limit exceeded',
        retry_after: Optional[int] = None,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        super().__init__(message, status_code=HTTP429)
        self.retry_after = retry_after


class CurrentsValidationError(CurrentsAPIError):
    """Invalid request parameters."""

    def __init__(
        self,
        message: str = 'Invalid request parameters',
        field: Optional[str] = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
        """
        super().__init__(message, status_code=HTTP400)
        self.field = field


class CurrentsServerError(CurrentsAPIError):
    """Server error."""

    def __init__(self, message: str = 'API server error') -> None:
        """Initialize server error.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=HTTP500)


class CurrentsConnectionError(CurrentsAPIError):
    """Connection failed."""

    def __init__(self, message: str = 'Failed to connect to Currents API') -> None:
        """Initialize connection error.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=None)


class CurrentsResponseError(CurrentsAPIError):
    """Invalid response format."""

    def __init__(self, message: str = 'Invalid API response format') -> None:
        """Initialize response error.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=None)
