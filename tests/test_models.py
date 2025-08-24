"""Tests for the Pydantic models."""

import os
import sys
from datetime import datetime

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from currents_news_client.models import (
    CategoryNewsParams,
    ErrorResponse,
    LatestNewsParams,
    NewsArticle,
    NewsResponse,
    SearchParams,
)


class TestNewsArticle:
    """Test the NewsArticle model."""

    def test_valid_news_article(self):
        """Test creating a valid news article."""
        article_data = {
            'id': 'test-id',
            'title': 'Test Article',
            'description': 'Test description',
            'url': 'https://example.com/article',
            'author': 'Test Author',
            'image': 'https://example.com/image.jpg',
            'language': 'en',
            'category': ['technology'],
            'published': '2024-01-01T12:00:00+00:00',
        }

        article = NewsArticle(**article_data)

        assert article.id == 'test-id'
        assert article.title == 'Test Article'
        assert article.description == 'Test description'
        assert str(article.url) == 'https://example.com/article'
        assert article.author == 'Test Author'
        assert article.image == 'https://example.com/image.jpg'
        assert article.language == 'en'
        assert article.category == ['technology']
        assert isinstance(article.published, datetime)

    def test_news_article_without_optional_fields(self):
        """Test creating a news article without optional fields."""
        article_data = {
            'id': 'test-id',
            'title': 'Test Article',
            'description': 'Test description',
            'url': 'https://example.com/article',
            'language': 'en',
            'category': [],
            'published': '2024-01-01T12:00:00+00:00',
        }

        article = NewsArticle(**article_data)

        assert article.author is None
        assert article.image is None
        assert article.category == []

    def test_invalid_url(self):
        """Test that invalid URLs raise an error."""
        article_data = {
            'id': 'test-id',
            'title': 'Test Article',
            'description': 'Test description',
            'url': 'not-a-url',
            'language': 'en',
            'category': [],
            'published': '2024-01-01T12:00:00+00:00',
        }

        with pytest.raises(ValueError):
            NewsArticle(**article_data)


class TestNewsResponse:
    """Test the NewsResponse model."""

    def test_valid_news_response(self):
        """Test creating a valid news response."""
        response_data = {
            'status': 'ok',
            'news': [
                {
                    'id': 'test-id',
                    'title': 'Test Article',
                    'description': 'Test description',
                    'url': 'https://example.com/article',
                    'language': 'en',
                    'category': [],
                    'published': '2024-01-01T12:00:00+00:00',
                },
            ],
        }

        response = NewsResponse(**response_data)

        assert response.status == 'ok'
        assert len(response.news) == 1
        assert response.total_count == 1
        assert isinstance(response.news[0], NewsArticle)

    def test_empty_news_response(self):
        """Test creating an empty news response."""
        response_data = {
            'status': 'ok',
            'news': [],
        }

        response = NewsResponse(**response_data)

        assert response.status == 'ok'
        assert response.total_count == 0
        assert response.news == []


class TestErrorResponse:
    """Test the ErrorResponse model."""

    def test_valid_error_response(self):
        """Test creating a valid error response."""
        error_data = {
            'status': 'error',
            'message': 'Something went wrong',
            'code': 500,
        }

        error = ErrorResponse(**error_data)

        assert error.status == 'error'
        assert error.message == 'Something went wrong'
        assert error.code == 500

    def test_error_response_without_code(self):
        """Test creating an error response without a code."""
        error_data = {
            'status': 'error',
            'message': 'Something went wrong',
        }

        error = ErrorResponse(**error_data)

        assert error.status == 'error'
        assert error.message == 'Something went wrong'
        assert error.code is None


class TestSearchParams:
    """Test the SearchParams model."""

    def test_valid_search_params(self):
        """Test creating valid search parameters."""
        search_params = SearchParams(
            keywords='technology',
            language='en',
            limit=10,
            domain='example.com',
        )

        assert search_params.keywords == 'technology'
        assert search_params.language == 'en'
        assert search_params.limit == 10
        assert search_params.domain == 'example.com'

    def test_search_params_defaults(self):
        """Test search parameters with default values."""
        search_params = SearchParams(keywords='test')

        assert search_params.keywords == 'test'
        assert search_params.language == 'en'
        assert search_params.limit == 20
        assert search_params.domain is None


class TestLatestNewsParams:
    """Test the LatestNewsParams model."""

    def test_valid_latest_news_params(self):
        """Test creating valid latest news parameters."""
        search_params = LatestNewsParams(language='es', limit=15)

        assert search_params.language == 'es'
        assert search_params.limit == 15

    def test_latest_news_params_defaults(self):
        """Test latest news parameters with default values."""
        search_params = LatestNewsParams()

        assert search_params.language == 'en'
        assert search_params.limit == 20


class TestCategoryNewsParams:
    """Test the CategoryNewsParams model."""

    def test_valid_category_news_params(self):
        """Test creating valid category news parameters."""
        search_params = CategoryNewsParams(
            category='technology',
            language='fr',
            limit=25,
        )

        assert search_params.category == 'technology'
        assert search_params.language == 'fr'
        assert search_params.limit == 25

    def test_category_news_params_defaults(self):
        """Test category news parameters with default values."""
        search_params = CategoryNewsParams(category='business')

        assert search_params.category == 'business'
        assert search_params.language == 'en'
        assert search_params.limit == 20
