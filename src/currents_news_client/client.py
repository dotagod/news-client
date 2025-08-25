"""Currents News API client."""

import os
import time
from types import TracebackType
from typing import Any, Dict, Optional, Type

import requests
from dotenv import load_dotenv

from .exceptions import (
    CurrentsAPIError,
    CurrentsAuthenticationError,
    CurrentsConnectionError,
    CurrentsRateLimitError,
    CurrentsResponseError,
    CurrentsServerError,
    CurrentsValidationError,
)
from .models import NewsResponse
from .types import (
    DEFAULT_LANGUAGE,
    DEFAULT_LIMIT,
    ERROR_MESSAGES,
    LATEST_NEWS_ENDPOINT,
    MAX_LIMIT,
    MIN_LIMIT,
    SEARCH_ENDPOINT,
)

HTTP401 = 401
HTTP400 = 400
HTTP429 = 429
HTTP500 = 500
REQUEST_TIMEOUT = 30

load_dotenv()


class _ParameterValidator:
    """Validates API request parameters."""

    def validate_language(self, language: str) -> None:
        """Check if language is supported.

        Args:
            language: Language code to validate

        Raises:
            CurrentsValidationError: If language is not supported
        """
        valid_languages = [
            'en',
            'es',
            'fr',
            'de',
            'it',
            'pt',
            'ru',
            'ar',
            'hi',
            'zh',
            'ja',
            'ko',
            'th',
            'vi',
        ]
        if language not in valid_languages:
            raise CurrentsValidationError(
                ERROR_MESSAGES['invalid_language'].format(language=language),
            )

    def validate_limit(self, limit: int) -> None:
        """Check if limit is within allowed range.

        Args:
            limit: Limit value to validate

        Raises:
            CurrentsValidationError: If limit is out of range
        """
        if limit < MIN_LIMIT or limit > MAX_LIMIT:
            raise CurrentsValidationError(ERROR_MESSAGES['limit_out_of_range'])

    def validate_category(self, category: str) -> None:
        """Check if category is supported.

        Args:
            category: Category to validate

        Raises:
            CurrentsValidationError: If category is not supported
        """
        valid_categories = [
            'world',
            'politics',
            'business',
            'technology',
            'sports',
            'entertainment',
            'health',
            'science',
            'regional',
            'hardware',
            'lifestyle',
            'travel',
        ]
        if category not in valid_categories:
            raise CurrentsValidationError(
                ERROR_MESSAGES['invalid_category'].format(category=category),
            )

    def validate_keywords(self, keywords: str) -> None:
        """Check if keywords are valid.

        Args:
            keywords: Search keywords to validate

        Raises:
            CurrentsValidationError: If keywords are empty or invalid
        """
        if not keywords or not keywords.strip():
            raise CurrentsValidationError(ERROR_MESSAGES['invalid_parameters'])

    def validate_params(
        self,
        language: str,
        limit: int,
        category: Optional[str] = None,
    ) -> None:
        """Validate common parameters.

        Args:
            language: Language code to validate
            limit: Limit value to validate
            category: Category to validate if provided
        """
        self.validate_language(language)
        self.validate_limit(limit)
        if category:
            self.validate_category(category)


class _ErrorRaiser:
    """Raises appropriate exceptions for different error types."""

    def raise_auth_error(self) -> None:
        """Raise authentication error.

        Raises:
            CurrentsAuthenticationError: For authentication failures
        """
        raise CurrentsAuthenticationError(ERROR_MESSAGES['invalid_api_key'])

    def raise_validation_error(self) -> None:
        """Raise validation error.

        Raises:
            CurrentsValidationError: For validation failures
        """
        raise CurrentsValidationError(ERROR_MESSAGES['invalid_parameters'])

    def raise_server_error(self) -> None:
        """Raise server error.

        Raises:
            CurrentsServerError: For server failures
        """
        raise CurrentsServerError(ERROR_MESSAGES['server_error'])

    def raise_generic_error(self, status_code: int, response: requests.Response) -> None:
        """Raise generic API error.

        Args:
            status_code: HTTP status code
            response: HTTP response object

        Raises:
            CurrentsAPIError: For generic HTTP errors
        """
        raise CurrentsAPIError('HTTP {0}: {1}'.format(status_code, response.reason))


class _HTTPErrorHandler:
    """Handles HTTP errors and response parsing."""

    def __init__(self) -> None:
        self._error_raiser = _ErrorRaiser()

    def handle_http_error(self, status_code: int, response: requests.Response) -> None:
        """Handle HTTP errors with appropriate exceptions.

        Args:
            status_code: HTTP status code
            response: HTTP response object
        """
        if status_code == HTTP401:
            self._error_raiser.raise_auth_error()
        elif status_code == HTTP429:
            self._handle_rate_limit_error(response)
        elif status_code == HTTP400:
            self._error_raiser.raise_validation_error()
        elif status_code >= HTTP500:
            self._error_raiser.raise_server_error()
        else:
            self._error_raiser.raise_generic_error(status_code, response)

    def parse_response_json(self, response: requests.Response) -> Any:
        """Parse JSON response safely.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON data

        Raises:
            CurrentsResponseError: If JSON parsing fails
        """
        try:
            return response.json()
        except ValueError:
            raise CurrentsResponseError(
                '{0}: Invalid JSON'.format(ERROR_MESSAGES['invalid_response']),
            )

    def _handle_rate_limit_error(self, response: requests.Response) -> None:
        """Handle rate limit errors.

        Args:
            response: HTTP response object

        Raises:
            CurrentsRateLimitError: With retry-after information
        """
        retry_after_str = response.headers.get('Retry-After')
        retry_after: Optional[int] = None
        if retry_after_str:
            try:
                retry_after = int(retry_after_str)
            except ValueError:
                retry_after = None
        raise CurrentsRateLimitError(
            ERROR_MESSAGES['rate_limit_exceeded'],
            retry_after=retry_after,
        )


class HTTPClient:
    """Handles HTTP requests, retries, and error handling."""

    def __init__(self, api_key: str, base_url: str) -> None:
        """Initialize the HTTP client.

        Args:
            api_key: API key for authentication
            base_url: API base URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.params = {'apiKey': api_key}

        self.max_retries = 3
        self.retry_delay = 1
        self._http_error_handler = _HTTPErrorHandler()

    def request(
        self,
        endpoint: str,
        request_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make API request with retry logic.

        Args:
            endpoint: API endpoint to call
            request_params: Query parameters

        Returns:
            Response data

        Raises:
            CurrentsConnectionError: If all retries fail
        """
        url = '{0}{1}'.format(self.base_url, endpoint)

        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url,
                    params=request_params,
                    timeout=REQUEST_TIMEOUT,
                )
            except requests.exceptions.RequestException:
                if attempt == self.max_retries - 1:
                    raise CurrentsConnectionError(ERROR_MESSAGES['connection_error'])
                time.sleep(self.retry_delay * (2 ** attempt))
                continue

            return self._handle_response(response)

        raise CurrentsConnectionError(ERROR_MESSAGES['connection_error'])

    def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            self.session.close()

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Process API response and handle errors.

        Args:
            response: HTTP response object

        Returns:
            Parsed response data

        Raises:
            CurrentsResponseError: For invalid response format
        """
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            self._http_error_handler.handle_http_error(response.status_code, response)

        response_data = self._http_error_handler.parse_response_json(response)

        if not isinstance(response_data, dict):
            raise CurrentsResponseError(ERROR_MESSAGES['invalid_response'])
        return response_data


class CurrentsClient:
    """Client for Currents News API."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = 'https://api.currentsapi.services/v1') -> None:
        """Initialize the client.

        Args:
            api_key: API key, or will look for NEWS_API_KEY env var
            base_url: API base URL

        Raises:
            CurrentsAuthenticationError: If no API key is provided
        """
        api_key = api_key or os.getenv('NEWS_API_KEY')
        if not api_key:
            raise CurrentsAuthenticationError(ERROR_MESSAGES['invalid_api_key'])

        self._http_client = HTTPClient(api_key, base_url)
        self._validator = _ParameterValidator()

    def get_latest_news(self, language: str = DEFAULT_LANGUAGE, limit: int = DEFAULT_LIMIT) -> NewsResponse:
        """Get latest news articles.

        Args:
            language: Language code for articles
            limit: Number of articles to return

        Returns:
            News response with articles
        """
        self._validator.validate_params(language, limit)

        request_params = {
            'language': language,
            'limit': limit,
        }

        response_data = self._http_client.request(LATEST_NEWS_ENDPOINT, request_params)
        return NewsResponse(**response_data)

    def search_news(
        self,
        keywords: str,
        language: str = DEFAULT_LANGUAGE,
        limit: int = DEFAULT_LIMIT,
        domain: Optional[str] = None,
    ) -> NewsResponse:
        """Search for news articles.

        Args:
            keywords: Search keywords
            language: Language code for articles
            limit: Number of articles to return
            domain: Domain to search in

        Returns:
            News response with articles
        """
        self._validator.validate_params(language, limit)
        self._validator.validate_keywords(keywords)

        request_params = {
            'keywords': keywords,
            'language': language,
            'limit': limit,
        }
        if domain:
            request_params['domain'] = domain

        response_data = self._http_client.request(SEARCH_ENDPOINT, request_params)
        return NewsResponse(**response_data)

    def get_category_news(
        self,
        category: str,
        language: str = DEFAULT_LANGUAGE,
        limit: int = DEFAULT_LIMIT,
    ) -> NewsResponse:
        """Get news articles by category.

        Args:
            category: News category
            language: Language code for articles
            limit: Number of articles to return

        Returns:
            News response with articles
        """
        self._validator.validate_params(language, limit, category)

        request_params = {
            'category': category,
            'language': language,
            'limit': limit,
        }

        response_data = self._http_client.request(SEARCH_ENDPOINT, request_params)
        return NewsResponse(**response_data)

    def __enter__(self) -> 'CurrentsClient':
        """Enter context manager.

        Returns:
            The CurrentsClient instance
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit context manager.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        self._http_client.close()
