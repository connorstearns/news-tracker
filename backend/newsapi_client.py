"""
NewsAPI client module for making requests to the NewsAPI everything endpoint.
"""

import os
import requests
from typing import Optional

NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"


def get_api_key() -> str:
    """Get the NewsAPI key from environment variables."""
    api_key = os.environ.get("NEWSAPI_KEY")
    if not api_key:
        raise ValueError("NEWSAPI_KEY environment variable is not set")
    return api_key


def newsapi_everything(
    q: str,
    from_date: str,
    to_date: str,
    language: str = "en",
    domains: Optional[str] = None,
    page_size: int = 100,
    page: int = 1
) -> dict:
    """
    Query the NewsAPI /everything endpoint.
    
    Args:
        q: Search query string (supports NewsAPI syntax like OR, AND, quotes)
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format
        language: Language code (default: "en")
        domains: Comma-separated list of domains to filter (optional)
        page_size: Number of results per page (max 100)
        page: Page number for pagination
    
    Returns:
        Parsed JSON response from NewsAPI
    
    Raises:
        requests.exceptions.RequestException: On network errors
        ValueError: If API key is not set
    """
    api_key = get_api_key()
    
    params = {
        "q": q,
        "from": from_date,
        "to": to_date,
        "language": language,
        "pageSize": page_size,
        "page": page,
        "apiKey": api_key,
        "sortBy": "publishedAt"
    }
    
    if domains:
        params["domains"] = domains
    
    response = requests.get(NEWSAPI_BASE_URL, params=params, timeout=30)
    
    return {
        "status_code": response.status_code,
        "data": response.json()
    }
