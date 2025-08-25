#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from currents_news_client.client import CurrentsClient


def main():
    """Run the example demonstrating the Currents News API client."""
    print('Currents News API Client - Example')
    print('=' * 40)

    # Check if API key is set
    if not os.getenv('NEWS_API_KEY'):
        print('NEWS_API_KEY not set')
        print('Set it first:')
        print("export NEWS_API_KEY='your_api_key_here'")
        print('\nGet a free key from: https://currentsapi.services/')
        return

    try:
        with CurrentsClient() as client:
            print('\nGetting latest news...')
            latest_news = client.get_latest_news('en', limit=3)
            print(f'Found {latest_news.total_count} articles')

            for index, article in enumerate(latest_news.news, 1):
                print(f'\n{index}. {article.title}')
                print(f'   Author: {article.author or "Unknown"}')
                print(f'   Category: {", ".join(article.category) if article.category else "Uncategorized"}')
                print(f'   Published: {article.published}')
                print(f'   URL: {article.url}')

            print('\nSearching for tech news...')
            tech_news = client.search_news('technology', limit=2)
            print(f'Found {tech_news.total_count} tech articles')

            # Tech news
            for index, article in enumerate(tech_news.news, 1):
                print(f'\n{index}. {article.title}')
                print(f'   Description: {article.description[:100]}...')
                print(f'   URL: {article.url}')

            print('\nGetting business news...')
            business_news = client.get_category_news('business', limit=2)
            print(f'Found {business_news.total_count} business articles')

            # Business news
            for index, article in enumerate(latest_news.news, 1):
                print(f'\n{index}. {article.title}')
                print(f'   Author: {article.author or "Unknown"}')
                print(f'   URL: {article.url}')

    except Exception as error:
        print(f'Error: {error}')


if __name__ == '__main__':
    main()
