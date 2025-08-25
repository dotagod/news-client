"""Types and constants for the client."""

from types import MappingProxyType
from typing import Literal

SUPPORTED_LANGUAGES = (
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
)

LanguageCode = Literal[
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

SUPPORTED_CATEGORIES = (
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
)

NewsCategory = Literal[
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

ResponseStatus = Literal['ok', 'error']
HTTPMethod = Literal['GET', 'POST', 'PUT', 'DELETE']
RateLimitHeaders = Literal[
    'X-RateLimit-Limit',
    'X-RateLimit-Remaining',
    'X-RateLimit-Reset',
]

DEFAULT_LANGUAGE: LanguageCode = 'en'
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
MIN_LIMIT = 1

LATEST_NEWS_ENDPOINT = '/latest-news'
SEARCH_ENDPOINT = '/search'

_LANGUAGE_SUPPORT_MSG = ' '.join([
    'Invalid language code. Supported: en, es, fr, de, it, pt, ru,',
    'ar, hi, zh, ja, ko, th, vi',
])
_CATEGORY_SUPPORT_MSG = ' '.join([
    'Invalid category. Supported: world, politics, business,',
    'technology, sports, entertainment, health, science, regional,',
    'hardware, lifestyle, travel',
])

ERROR_MESSAGES = MappingProxyType({
    'invalid_api_key': 'Invalid API key provided',
    'rate_limit_exceeded': 'API rate limit exceeded. Please try again later.',
    'invalid_parameters': 'Invalid request parameters provided',
    'server_error': 'API server error. Please try again later.',
    'connection_error': 'Failed to connect to Currents API',
    'invalid_response': 'Invalid response from API',
    'missing_required_field': 'Missing required field: {field}',
    'invalid_language': _LANGUAGE_SUPPORT_MSG,
    'invalid_category': _CATEGORY_SUPPORT_MSG,
    'limit_out_of_range': 'Limit must be between 1 and 100',
})

HTTP_STATUS_CODES = MappingProxyType({
    200: 'OK',
    400: 'Bad Request',
    401: 'Unauthorized',
    429: 'Too Many Requests',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
})
