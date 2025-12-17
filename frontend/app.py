"""
Streamlit frontend for querying NewsAPI through the FastAPI backend.
Includes collapsible articles and simple topic categorization + filtering.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List

import requests
import streamlit as st


# -----------------------------
# Topic categorization (simple rules)
# -----------------------------
TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "Healthcare Policy": [
        "medicare", "medicaid", "aca", "affordable care act", "health policy",
        "health reform", "insurance coverage", "uninsured"
    ],
    "Hospitals & Clinics": [
        "hospital", "clinic", "emergency room", "er", "icu", "inpatient",
        "outpatient", "medical center"
    ],
    "Pharmaceuticals": [
        "drug", "pharmaceutical", "medication", "fda", "prescription", "vaccine",
        "pfizer", "moderna", "pharma"
    ],
    "Mental Health": [
        "mental health", "depression", "anxiety", "psychiatry", "therapy",
        "counseling", "suicide", "behavioral health"
    ],
    "Public Health": [
        "public health", "cdc", "outbreak", "epidemic", "pandemic", "disease",
        "infection", "prevention"
    ],
    "Rural Health": [
        "rural health", "rural hospital", "rural clinic", "underserved", "remote"
    ],
    "Technology & AI": [
        "artificial intelligence", "ai", "machine learning", "technology",
        "digital health", "telehealth", "telemedicine"
    ],
    "Workforce": [
        "staffing", "nurse", "nursing", "physician", "doctor", "workforce",
        "shortage", "burnout", "healthcare worker"
    ],
    "Research": [
        "study", "research", "clinical trial", "findings", "scientists", "researchers"
    ],
    "Costs & Pricing": [
        "cost", "costs", "price", "pricing", "spending", "expensive", "affordable",
        "billing", "debt", "payment"
    ],
}
OTHER_TOPIC = "Other/Uncategorized"


def classify_topics(article: Dict) -> List[str]:
    """Classify an article into topics based on keywords in title + description."""
    text = f"{article.get('title', '')} {article.get('description', '')}".lower()
    topics: List[str] = []

    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(k.lower() in text for k in keywords):
            topics.append(topic)

    return topics if topics else [OTHER_TOPIC]


def format_published_date(published: str) -> str:
    """Format ISO timestamps from NewsAPI for display."""
    if not published:
        return "Unknown date"
    try:
        dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return published


def render_article(article: Dict, index: int, show_topics: bool = True) -> None:
    """Render a single article as a collapsed expander card."""
    title = article.get("title", "No title")
    source = article.get("source", "Unknown source")
    published_display = format_published_date(article.get("publishedAt", ""))
    url = article.get("url", "")
    description = article.get("description", "")
    content = article.get("content", "")

    topics = article.get("_topics") or classify_topics(article)

    short_title = title if len(title) <= 90 else (title[:90] + "…")
    header = f"{index}. {short_title} | {source} | {published_display}"

    with st.expander(header, expanded=False):
        if show_topics and topics:
            st.markdown("**Topics:** " + " ".join([f"`{t}`" for t in topics]))

        st.markdown(f"**Source:** {source}")
        st.markdown(f"**Published:** {published_display}")

        if url:
            # link_button is nicer if available; markdown link also works.
            try:
                st.link_button("Read full article", url)
            except Exception:
                st.markdown(f"[Read full article]({url})")

        if description:
            st.markdown("**Description**")
            st.write(description)

        if content:
            st.markdown("**Content preview**")
            st.write(content)


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="NewsAPI Query Tool", page_icon="📰", layout="wide")

st.title("📰 NewsAPI Query Tool")
st.markdown("Search for news articles by keyword and date range using NewsAPI.")


# -----------------------------
# Backend URL config
# -----------------------------
backend_url = os.getenv("BACKEND_URL")

if not backend_url:
    st.sidebar.header("Configuration")
    backend_url = st.sidebar.text_input(
        "Backend URL",
        value="http://localhost:8000",
        help="Used only for local development (Streamlit Cloud should use BACKEND_URL secret).",
    )
    st.sidebar.markdown("---")

backend_url = (backend_url or "").rstrip("/")


# -----------------------------
# Sidebar topic controls
# -----------------------------
st.sidebar.header("Topic Filters")
all_topics = list(TOPIC_KEYWORDS.keys()) + [OTHER_TOPIC]

selected_topics = st.sidebar.multiselect(
    "Filter by topic",
    options=all_topics,
    default=[],
    help="Select topics to filter results (leave empty to show all).",
)

group_by_topic = st.sidebar.toggle(
    "Group results by topic",
    value=False,
    help="If enabled, articles will be grouped under topic headings.",
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Example Queries")
st.sidebar.markdown(
    """
- `healthcare AND medicare`
- `(hospital OR clinic) AND staffing`
- `"artificial intelligence"`
- `technology OR innovation`
"""
)


# -----------------------------
# Search inputs
# -----------------------------
st.header("Search Parameters")

col1, col2 = st.columns(2)
with col1:
    query = st.text_input(
        "Keyword Query",
        value='healthcare OR "health care"',
        help="Supports NewsAPI syntax: AND, OR, quotes for exact phrases",
    )

with col2:
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    date_range = st.date_input(
        "Date Range",
        value=(week_ago, today),
        help="Select start and end dates for your search",
    )

col3, col4 = st.columns(2)
with col3:
    domains = st.text_input(
        "Domains Filter (optional)",
        value="",
        placeholder="kffhealthnews.org,reuters.com",
        help="Comma-separated list of domains to filter results",
    )

with col4:
    limit = st.slider(
        "Number of Results",
        min_value=1,
        max_value=50,
        value=20,
        help="Maximum number of articles to retrieve",
    )

st.markdown("---")


# -----------------------------
# Search action
# -----------------------------
if st.button("🔍 Search", type="primary"):
    if not backend_url:
        st.error("Backend URL is not set.")
    elif not query.strip():
        st.error("Please enter a search query.")
    elif not isinstance(date_range, tuple) or len(date_range) != 2:
        st.error("Please select both a start and end date.")
    else:
        from_date = date_range[0].strftime("%Y-%m-%d")
        to_date = date_range[1].strftime("%Y-%m-%d")

        params = {"q": query, "from": from_date, "to": to_date, "limit": limit}
        if domains.strip():
            params["domains"] = domains.strip()

        with st.spinner("Searching for articles..."):
            try:
                response = requests.get(f"{backend_url}/search", params=params, timeout=60)

                if response.status_code == 200:
                    data = response.json()

                    if data.get("ok"):
                        total = data.get("totalResults", 0)
                        articles = data.get("articles", []) or []

                        # attach topics once
                        for a in articles:
                            a["_topics"] = classify_topics(a)

                        # apply topic filtering
                        if selected_topics:
                            articles = [
                                a for a in articles
                                if any(t in selected_topics for t in a["_topics"])
                            ]

                        st.success(f"**Total Results Found: {total:,}** (from {from_date} to {to_date})")

                        if not articles:
                            st.info("No articles match your search (or selected topic filters).")
                        elif group_by_topic:
                            topics_with_articles: Dict[str, List[Dict]] = {}
                            for a in articles:
                                for t in a["_topics"]:
                                    if selected_topics and t not in selected_topics:
                                        continue
                                    topics_with_articles.setdefault(t, []).append(a)

                            for topic in sorted(topics_with_articles.keys()):
                                topic_articles = topics_with_articles[topic]
                                st.subheader(f"{topic} ({len(topic_articles)} article(s))")
                                for i, a in enumerate(topic_articles, 1):
                                    render_article(a, i, show_topics=False)
                        else:
                            st.subheader(f"Showing {len(articles)} article(s)")
                            for i, a in enumerate(articles, 1):
                                render_article(a, i, show_topics=True)

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
