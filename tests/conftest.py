"""Test fixtures for the Currents News API client tests."""

from unittest.mock import Mock

import pytest
import requests


@pytest.fixture
def mock_response():
    """Create a mock successful response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        'status': 'ok',
        'news': [
            {
                'id': 'test-id-1',
                'title': 'Test News Article 1',
                'description': 'This is a test news article description',
                'url': 'https://example.com/article1',
                'author': 'Test Author',
                'image': 'https://example.com/image1.jpg',
                'language': 'en',
                'category': ['technology'],
                'published': '2024-01-01T12:00:00+00:00',
            },
            {
                'id': 'test-id-2',
                'title': 'Test News Article 2',
                'description': 'Another test news article description',
                'url': 'https://example.com/article2',
                'author': 'Another Author',
                'image': None,
                'language': 'en',
                'category': ['business', 'technology'],
                'published': '2024-01-01T13:00:00+00:00',
            },
        ],
    }
    mock.raise_for_status.return_value = None
    return mock


@pytest.fixture
def mock_error_response():
    """Create a mock error response."""
    mock = Mock()
    mock.status_code = 401
    mock.json.return_value = {
        'status': 'error',
        'message': 'Invalid API key',
    }
    mock.raise_for_status.side_effect = requests.exceptions.HTTPError(
        '401 Client Error: Unauthorized',
    )
    return mock


@pytest.fixture
def mock_rate_limit_response():
    """Create a mock rate limit response."""
    mock = Mock()
    mock.status_code = 429
    mock.headers = {'Retry-After': '60'}
    mock.json.return_value = {
        'status': 'error',
        'message': 'Rate limit exceeded',
    }
    mock.raise_for_status.side_effect = requests.exceptions.HTTPError(
        '429 Client Error: Too Many Requests',
    )
    return mock


@pytest.fixture
def sample_news_data():
    """Create sample news data for testing."""
    return {
        'status': 'ok',
        'news': [
            {
                'id': 'sample-id-1',
                'title': 'Sample Technology News',
                'description': 'A sample technology news article',
                'url': 'https://example.com/tech-news',
                'author': 'Tech Writer',
                'image': 'https://example.com/tech-image.jpg',
                'language': 'en',
                'category': ['technology'],
                'published': '2024-01-01T10:00:00+00:00',
            },
        ],
    }


@pytest.fixture
def valid_api_key():
    """Create a valid API key for testing."""
    return 'valid-api-key-12345'


@pytest.fixture
def invalid_api_key():
    """Create an invalid API key for testing."""
    return 'invalid-api-key'
