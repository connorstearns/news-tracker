"""
Streamlit frontend for querying NewsAPI through the FastAPI backend.
"""

from datetime import datetime, timedelta

import requests
import streamlit as st
import os



st.set_page_config(
    page_title="NewsAPI Query Tool",
    page_icon="📰",
    layout="wide"
)

st.title("📰 NewsAPI Query Tool")
st.markdown("Search for news articles by keyword and date range using NewsAPI.")

backend_url = os.getenv("BACKEND_URL")

if not backend_url:
    backend_url = st.sidebar.text_input(
        "Backend URL",
        value="http://localhost:8000",
        help="Used only for local development"
    )

backend_url = backend_url.rstrip("/")

st.header("Search Parameters")

col1, col2 = st.columns(2)

with col1:
    query = st.text_input(
        "Keyword Query",
        value='healthcare OR "health care"',
        help="Supports NewsAPI syntax: AND, OR, quotes for exact phrases"
    )

with col2:
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    date_range = st.date_input(
        "Date Range",
        value=(week_ago, today),
        help="Select start and end dates for your search"
    )

col3, col4 = st.columns(2)

with col3:
    domains = st.text_input(
        "Domains Filter (optional)",
        value="",
        placeholder="kffhealthnews.org,reuters.com",
        help="Comma-separated list of domains to filter results"
    )

with col4:
    limit = st.slider(
        "Number of Results",
        min_value=1,
        max_value=50,
        value=20,
        help="Maximum number of articles to retrieve"
    )

st.markdown("---")

if st.button("🔍 Search", type="primary"):
    if not query.strip():
        st.error("Please enter a search query.")
    elif not isinstance(date_range, tuple) or len(date_range) != 2:
        st.error("Please select both a start and end date.")
    else:
        from_date = date_range[0].strftime("%Y-%m-%d")
        to_date = date_range[1].strftime("%Y-%m-%d")

        params = {
            "q": query,
            "from": from_date,
            "to": to_date,
            "limit": limit
        }

        if domains.strip():
            params["domains"] = domains.strip()

        with st.spinner("Searching for articles..."):
            try:
                response = requests.get(
                    f"{backend_url}/search",
                    params=params,
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()

                    if data.get("ok"):
                        total = data.get("totalResults", 0)
                        articles = data.get("articles", [])

                        st.success(f"**Total Results Found: {total:,}** (from {from_date} to {to_date})")

                        if articles:
                            st.subheader(f"Showing {len(articles)} article(s)")

                            for i, article in enumerate(articles, 1):
                                title = article.get("title", "No title")
                                source = article.get("source", "Unknown source")
                                published = article.get("publishedAt", "")
                                url = article.get("url", "")

                                if published:
                                    try:
                                        dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                                        published_display = dt.strftime("%Y-%m-%d %H:%M")
                                    except:
                                        published_display = published
                                else:
                                    published_display = "Unknown date"

                                with st.container():
                                    st.markdown(f"**{i}. [{title}]({url})**")
                                    st.caption(f"📌 {source} | 🕐 {published_display}")
                                    st.markdown("---")
                        else:
                            st.info("No articles found for this query and date range.")
                    else:
                        error = data.get("error", "Unknown error")
                        if isinstance(error, dict):
                            error_msg = error.get("message", str(error))
                        else:
                            error_msg = str(error)
                        st.error(f"API Error: {error_msg}")
                else:
                    st.error(f"Backend returned status code: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error(
                    f"Could not connect to backend at {backend_url}. "
                    "Make sure the backend server is running."
                )
            except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.sidebar.markdown("### Example Queries")
st.sidebar.markdown("""
- `healthcare AND medicare`
- `(hospital OR clinic) AND staffing`
- `"artificial intelligence"`
- `technology OR innovation`
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### Tips")
st.sidebar.markdown("""
- Use **AND** to require both terms
- Use **OR** for either term
- Use **quotes** for exact phrases
- Add domains to filter by source
- Select a date range to search across multiple days
""")
