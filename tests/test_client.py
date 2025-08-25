import os
import sys
from unittest.mock import Mock, patch

import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from currents_news_client.client import CurrentsClient
from currents_news_client.exceptions import (
    CurrentsAuthenticationError,
    CurrentsConnectionError,
    CurrentsRateLimitError,
    CurrentsResponseError,
    CurrentsServerError,
    CurrentsValidationError,
)


class TestCurrentsClient:
    """Test the CurrentsClient class."""

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key(self):
        """Test client initialization without API key raises error."""
        with pytest.raises(CurrentsAuthenticationError):
            CurrentsClient()

    @patch('src.currents_news_client.client.requests.Session')
    def test_get_latest_news_success(self, mock_session, mock_response, valid_api_key):
        """Test successful latest news retrieval."""
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_instance.params = {}
        mock_session.return_value = mock_session_instance

        client = CurrentsClient(valid_api_key)
        response = client.get_latest_news('en', limit=5)

        assert response.status == 'ok'
        assert len(response.news) == 2
        assert response.total_count == 2
        assert response.news[0].title == 'Test News Article 1'

    @patch('src.currents_news_client.client.requests.Session')
    def test_search_news_success(self, mock_session, mock_response, valid_api_key):
        """Test successful news search."""
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_instance.params = {}
        mock_session.return_value = mock_session_instance

        client = CurrentsClient(valid_api_key)
        response = client.search_news('technology', limit=3)

        assert response.status == 'ok'
        assert len(response.news) == 2
        assert response.news[0].title == 'Test News Article 1'

    @patch('src.currents_news_client.client.requests.Session')
    def test_get_category_news_success(self, mock_session, mock_response, valid_api_key):
        """Test successful category news retrieval."""
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_instance.params = {}
        mock_session.return_value = mock_session_instance

        client = CurrentsClient(valid_api_key)
        response = client.get_category_news('technology', limit=3)

        assert response.status == 'ok'
        assert len(response.news) == 2
        assert response.news[0].title == 'Test News Article 1'

    @patch('src.currents_news_client.client.requests.Session')
    def test_validation_errors(self, mock_session, valid_api_key):
        """Test validation error handling."""
        mock_session_instance = Mock()
        mock_session_instance.params = {}
        mock_session.return_value = mock_session_instance

        client = CurrentsClient(valid_api_key)

        # Test various validation failures
        with pytest.raises(CurrentsValidationError):
            client.get_latest_news('invalid_language')

        with pytest.raises(CurrentsValidationError):
            client.get_latest_news('en', limit=0)

        with pytest.raises(CurrentsValidationError):
            client.get_latest_news('en', limit=101)

        with pytest.raises(CurrentsValidationError):
            client.get_category_news('invalid_category')

        with pytest.raises(CurrentsValidationError):
            client.search_news('')

    @patch('src.currents_news_client.client.requests.Session')
    def test_authentication_error(self, mock_session, mock_error_response, invalid_api_key):
        """Test authentication error handling."""
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_error_response
        mock_session_instance.params = {}
        mock_session.return_value = mock_session_instance

        client = CurrentsClient(invalid_api_key)

        with pytest.raises(CurrentsAuthenticationError):
            client.get_latest_news('en')

    @patch('src.currents_news_client.client.requests.Session')
    def test_rate_limit_error(self, mock_session, mock_rate_limit_response, valid_api_key):
        """Test rate limit error handling."""
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_rate_limit_response
        mock_session_instance.params = {}
        mock_session.return_value = mock_session_instance

        client = CurrentsClient(valid_api_key)

        with pytest.raises(CurrentsRateLimitError):
            client.get_latest_news('en')

    @patch('src.currents_news_client.client.requests.Session')
    def test_server_error(self, mock_session, valid_api_key):
        """Test server error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {'status': 'error', 'message': 'Server error'}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            '500 Server Error: Internal Server Error',
        )

        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_instance.params = {}
        mock_session.return_value = mock_session_instance

        client = CurrentsClient(valid_api_key)

        with pytest.raises(CurrentsServerError):
            client.get_latest_news('en')

    def test_context_manager(self, valid_api_key):
        """Test client as context manager."""
        with CurrentsClient(valid_api_key) as client:
            assert isinstance(client, CurrentsClient)

    @patch('src.currents_news_client.client.requests.Session')
    def test_retry_mechanism(self, mock_session, valid_api_key):
        """Test retry mechanism for failed requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok', 'news': []}
        mock_response.raise_for_status.return_value = None

        mock_session_instance = Mock()
        mock_session_instance.get.side_effect = [
            requests.exceptions.RequestException('Connection failed'),
            requests.exceptions.RequestException('Connection failed'),
            mock_response,
        ]
        mock_session_instance.params = {}
        mock_session.return_value = mock_session_instance

        client = CurrentsClient(valid_api_key)
        response = client.get_latest_news('en')

        assert response.status == 'ok'
        assert mock_session_instance.get.call_count == 3

    @patch('src.currents_news_client.client.requests.Session')
    def test_max_retries_exceeded(self, mock_session, valid_api_key):
        """Test behavior when max retries are exceeded."""
        mock_session_instance = Mock()
        mock_session_instance.get.side_effect = requests.exceptions.RequestException('Connection failed')
        mock_session_instance.params = {}
        mock_session.return_value = mock_session_instance

        client = CurrentsClient(valid_api_key)

        with pytest.raises(CurrentsConnectionError):
            client.get_latest_news('en')

        assert mock_session_instance.get.call_count == 3
