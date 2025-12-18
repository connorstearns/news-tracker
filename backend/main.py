"""
FastAPI backend service for querying NewsAPI.
Provides endpoints for health check, article count, and article search.
"""

import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from newsapi_client import newsapi_everything

app = FastAPI(
    title="NewsAPI Query Service",
    description="Backend service for querying NewsAPI articles by keyword and date range",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Validate that the NEWSAPI_KEY is set on startup."""
    api_key = os.environ.get("NEWSAPI_KEY")
    if not api_key:
        raise RuntimeError(
            "NEWSAPI_KEY environment variable is not set! "
            "Please add it to Replit Secrets before starting the application."
        )


def validate_date(date_str: str) -> bool:
    """Validate that date is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"ok": True}


@app.get("/count")
async def get_count(
    q: str = Query(..., description="Keyword query string"),
    from_date: str = Query(..., alias="from", description="Start date in YYYY-MM-DD format"),
    to_date: str = Query(..., alias="to", description="End date in YYYY-MM-DD format"),
    language: str = Query("en", description="Language code"),
    domains: Optional[str] = Query(None, description="Comma-separated domains to filter")
):
    """
    Get the total count of articles matching the query for a date range.
    """
    if not os.environ.get("NEWSAPI_KEY"):
        return {
            "ok": False,
            "error": "NEWSAPI_KEY is not configured. Please add it to Replit Secrets."
        }
    
    if not validate_date(from_date):
        return {
            "ok": False,
            "error": f"Invalid from date format: {from_date}. Expected YYYY-MM-DD."
        }
    
    if not validate_date(to_date):
        return {
            "ok": False,
            "error": f"Invalid to date format: {to_date}. Expected YYYY-MM-DD."
        }

    try:
        result = newsapi_everything(
            q=q,
            from_date=from_date,
            to_date=to_date,
            language=language,
            domains=domains,
            page_size=min(limit, 100),
            page=1,
            title_only=True,   # 👈 ADD THIS
        )

        if result["status_code"] != 200:
            return {
                "ok": False,
                "error": result["data"],
                "status_code": result["status_code"]
            }
        
        return {
            "ok": True,
            "q": q,
            "from": from_date,
            "to": to_date,
            "totalResults": result["data"].get("totalResults", 0)
        }
        
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }


@app.get("/search")
async def search_articles(
    q: str = Query(..., description="Keyword query string"),
    from_date: str = Query(..., alias="from", description="Start date in YYYY-MM-DD format"),
    to_date: str = Query(..., alias="to", description="End date in YYYY-MM-DD format"),
    language: str = Query("en", description="Language code"),
    domains: Optional[str] = Query(None, description="Comma-separated domains to filter"),
    limit: int = Query(20, ge=1, le=100, description="Number of articles to return (1-100)")
):
    """
    Search for articles matching the query for a date range.
    Returns article details including title, source, publishedAt, and URL.
    """
    if not os.environ.get("NEWSAPI_KEY"):
        return {
            "ok": False,
            "error": "NEWSAPI_KEY is not configured. Please add it to Replit Secrets."
        }
    
    if not validate_date(from_date):
        return {
            "ok": False,
            "error": f"Invalid from date format: {from_date}. Expected YYYY-MM-DD."
        }
    
    if not validate_date(to_date):
        return {
            "ok": False,
            "error": f"Invalid to date format: {to_date}. Expected YYYY-MM-DD."
        }
    
    limit = max(1, min(100, limit))
    
    try:
        result = newsapi_everything(
            q=q,
            from_date=from_date,
            to_date=to_date,
            language=language,
            domains=domains,
            page_size=limit,
            page=1
        )
        
        if result["status_code"] != 200:
            return {
                "ok": False,
                "error": result["data"],
                "status_code": result["status_code"]
            }
        
        raw_articles = result["data"].get("articles", [])
        articles = [
            {
                "title": article.get("title", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "publishedAt": article.get("publishedAt", ""),
                "url": article.get("url", "")
            }
            for article in raw_articles[:limit]
        ]
        
        return {
            "ok": True,
            "q": q,
            "from": from_date,
            "to": to_date,
            "totalResults": result["data"].get("totalResults", 0),
            "articles": articles
        }
        
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
