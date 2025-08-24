# Currents News API Client

## What This Does

This client wraps the Currents News API and gives you three main ways to get news:

- **Latest News**: Get the most recent articles in your language
- **Search**: Find articles by keywords or topics
- **Category-based**: Get news from specific categories like tech, business, sports, etc.

## Features

- **Multi-language support** - Works with 15+ languages (English, Spanish, French, German, etc.)
- **Smart error handling** - Handles API errors, rate limits, and connection issues gracefully
- **Type safety** - Full type hints and validation with Pydantic models
- **Context manager** - Clean resource management with `with` statements
- **Retry logic** - Automatically retries failed requests
- **Parameter validation** - Checks inputs before making API calls

## Quick Start

### 1. Get Your API Key

You'll need an API key from [Currents News API](https://currentsapi.services/). 

### 2. Install the Client

```bash
git clone <your-repo-url>
cd currents-news-client

pip install -r requirements.txt
```

### 3. Set Up Your API Key

```bash
export NEWS_API_KEY="your_actual_api_key_here"

```

### 4. Start Using It

```python
from currents_news_client import CurrentsClient

# Get the latest news
with CurrentsClient() as client:
    news = client.get_latest_news("en", limit=5)
    print(f"Found {news.total_count} articles")
    
    for article in news.news:
        print(f"- {article.title}")
        print(f"  Published: {article.published.strftime('%Y-%m-%d')}")
        print(f"  URL: {article.url}")
```

## API Methods

### Get Latest News
```python
latest = client.get_latest_news("en", limit=10)
```
Gets the most recent news articles. Works with 15+ languages.

### Search for News
```python
results = client.search_news("artificial intelligence", limit=20)
```
Finds articles with specific keywords. You can also filter by domain.

### Get News by Category
```python
tech_news = client.get_news_by_category("technology", limit=15)
```
Gets articles from categories like:
- `world`, `politics`, `business`
- `technology`, `sports`, `entertainment`
- `health`, `science`, `regional`

## Error Handling

The client handles errors gracefully:

- **Invalid API key** → Clear error message
- **Rate limiting** → Automatic retry with backoff
- **Network issues** → Retry logic for failed connections
- **Invalid parameters** → Validation before API calls
- **Server errors** → Proper error classification

## Development

### Running Tests
```bash
pip install -r requirements.txt

pytest tests/

mypy src/currents_news_client/

python3 -m flake8 src/ --config setup.cfg
```

### Project Structure
```
src/currents_news_client/
├── client.py          # Main client class
├── models.py          # Pydantic models
├── exceptions.py      # Custom errors
└── types.py           # Type definitions

tests/                 # Test suite
examples/              # Usage examples
```

## Code Quality

This project follows good practices:

- **Type checking**: Full mypy compliance with strict typing
- **Linting**: Follows wemake-python-styleguide (0.19.2)
- **Testing**: Good test coverage with pytest
- **Documentation**: Clear docstrings and examples

## Examples

Check out the `examples/` directory for more usage patterns, or run the demo:

```bash
python examples/basic_usage.py
```

## API Documentation

For detailed info about the API, see the [official documentation](https://currentsapi.services/en/docs/).
