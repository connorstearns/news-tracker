# NewsAPI Query Tool

A full-stack application for querying NewsAPI to search for news articles by keyword and date.

## Features

- **FastAPI Backend**: RESTful API service that wraps NewsAPI
- **Streamlit Frontend**: User-friendly interface for searching articles
- **Secure API Key Management**: Uses Replit Secrets for NEWSAPI_KEY
- **Flexible Search**: Supports NewsAPI query syntax (AND, OR, quotes)
- **Domain Filtering**: Optional filtering by news source domains

## Setup

### 1. Get a NewsAPI Key

1. Go to [https://newsapi.org/](https://newsapi.org/)
2. Sign up for a free account
3. Copy your API key from the dashboard

### 2. Add NEWSAPI_KEY to Replit Secrets

1. In your Replit project, click on "Secrets" in the Tools panel (or press Ctrl+Shift+S)
2. Click "New Secret"
3. Set the key as `NEWSAPI_KEY`
4. Paste your NewsAPI key as the value
5. Click "Add Secret"

### 3. Run the Application

Click the "Run" button in Replit. This will start both:
- Backend API on port 8000
- Streamlit frontend on port 5000

## API Endpoints

### Health Check
```
GET /health
Response: { "ok": true }
```

### Count Articles
```
GET /count?q=healthcare&from=2024-12-10&to=2024-12-15&language=en&domains=reuters.com
Response: {
  "ok": true,
  "q": "healthcare",
  "from": "2024-12-10",
  "to": "2024-12-15",
  "totalResults": 123
}
```

### Search Articles
```
GET /search?q=healthcare&from=2024-12-10&to=2024-12-15&language=en&limit=20
Response: {
  "ok": true,
  "q": "healthcare",
  "from": "2024-12-10",
  "to": "2024-12-15",
  "totalResults": 123,
  "articles": [
    {
      "title": "Article Title",
      "source": "Source Name",
      "publishedAt": "2024-12-15T10:30:00Z",
      "url": "https://..."
    }
  ]
}
```

## Example Queries

The search supports NewsAPI query syntax:

| Query | Description |
|-------|-------------|
| `healthcare AND medicare` | Articles containing both terms |
| `(hospital OR clinic) AND staffing` | Articles about hospital or clinic staffing |
| `"artificial intelligence"` | Exact phrase match |
| `technology OR innovation` | Articles with either term |

### Domain Filter Examples

Filter results to specific news sources:
- `reuters.com`
- `kffhealthnews.org,reuters.com` (multiple domains)
- `bbc.co.uk,cnn.com`

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── newsapi_client.py    # NewsAPI client module
│   └── requirements.txt     # Backend dependencies
├── frontend/
│   ├── app.py               # Streamlit application
│   └── requirements.txt     # Frontend dependencies
├── .gitignore
├── README.md
└── run.sh                   # Startup script
```

## Local Development

If running locally (outside Replit):

1. Create a `.env` file with your API key:
   ```
   NEWSAPI_KEY=your_api_key_here
   ```

2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   pip install -r frontend/requirements.txt
   ```

3. Start the backend:
   ```bash
   cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. Start the frontend (in another terminal):
   ```bash
   streamlit run frontend/app.py --server.port 8501
   ```

## Notes

- NewsAPI free tier has limitations (100 requests/day, articles from last month only)
- The backend validates date format (YYYY-MM-DD) and limit (1-100)
- Timeout is set to 30 seconds for API requests
