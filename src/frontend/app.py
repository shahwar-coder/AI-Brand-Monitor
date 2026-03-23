"""
AI Brand Monitoring Dashboard
------------------------------
Streamlit entry point. Handles UI, state management, and orchestrates
calls to backend modules (data_sources, ai_analysis, reporting).
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import plotly.express as px

from backend.database import initialize_database, get_unanalyzed_mentions_by_brand, update_mention_analysis
from backend.data_sources import fetch_hackernews_mentions
from backend.ai_analysis import get_sentiment, get_topic
from backend.reporting import (
    get_sentiment_distribution,
    get_topic_distribution,
    generate_brand_summary,
    get_mentions_table,
)

# --------------------------------------
# App bootstrap (runs once per process)
# --------------------------------------

# database initialization
initialize_database()

# page configuration
st.set_page_config(
    page_title="AI Brand Monitor",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Minimal custom CSS — tightens Streamlit's default chrome
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { background: #0f1117; }
        [data-testid="stSidebar"] * { color: #e8e8e8 !important; }
        .block-container { padding-top: 2rem; }
        div[data-testid="stMetric"] { background: #1a1d27; border-radius: 8px; padding: 1rem; }
        div[data-testid="stMetricLabel"] p { color: #9ca3af; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------
# Session state initialisation — done once, never reset mid-run
# --------------------------------------------------------------

DEFAULTS = {
    "current_brand": "",
    "mentions_fetched": False,
    "analysis_completed": False,
    "fetch_count": 0,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def _reset_brand_state() -> None:
    """Clear analysis state when the brand changes."""
    st.session_state.mentions_fetched = False
    st.session_state.analysis_completed = False
    st.session_state.fetch_count = 0
    st.cache_data.clear()


# --------
# Sidebar
# --------

with st.sidebar:
    st.markdown("## 📡 Brand Monitor")
    st.caption("Powered by Hacker News + local LLM")
    st.divider()

    brand_input = st.text_input(
        "Brand name",
        placeholder="e.g. OpenAI, Supabase, Linear …",
        help="The tool will search Hacker News for this exact term (case-insensitive).",
    )

    # Detect brand change and reset state automatically
    if brand_input and brand_input != st.session_state.current_brand:
        _reset_brand_state()
        st.session_state.current_brand = brand_input

    st.divider()

    fetch_btn = st.button(
        "🔍 Fetch Mentions",
        use_container_width=True,
        disabled=not brand_input,
    )

    analyze_btn = st.button(
        "🤖 Run AI Analysis",
        use_container_width=True,
        disabled=not st.session_state.mentions_fetched,
        help="Fetch mentions first before running analysis.",
    )

    st.divider()
    st.markdown(
        """
        **How to use**
        1. Type a brand name above
        2. Click **Fetch Mentions**
        3. Click **Run AI Analysis**
        4. Explore charts & insights
        """
    )

# -------
# Header
# -------

brand = st.session_state.current_brand  # convenience alias — stable within this run

st.title("📊 AI Brand Monitoring Dashboard")

if brand:
    st.caption(f"Showing results for **{brand}**")
else:
    st.caption("Enter a brand name in the sidebar to get started.")

# ----------------------
# Fetch Mentions action
# ----------------------

if fetch_btn:
    # brand_input is guaranteed non-empty (button is disabled otherwise)
    with st.spinner(f"Fetching latest Hacker News mentions for **{brand_input}** …"):
        count = fetch_hackernews_mentions(brand_input)

    st.session_state.fetch_count = count
    st.session_state.mentions_fetched = True
    st.session_state.current_brand = brand_input
    st.session_state.analysis_completed = False  # new fetches invalidate prior analysis view
    st.cache_data.clear()
    st.rerun()  # re-render so the sidebar success badge and button states update

# -----------------------
# Run AI Analysis action
# -----------------------

if analyze_btn:
    mentions = get_unanalyzed_mentions_by_brand(brand)

    if not mentions:
        st.info("✅ All mentions are already analysed — nothing new to process.")
    else:
        total = len(mentions)
        st.write(f"Analysing **{total}** mention(s) …")
        progress = st.progress(0)
        status = st.empty()

        for i, mention in enumerate(mentions, start=1):
            mention_id = mention["id"]
            title = mention.get("title") or ""
            text = mention.get("text") or ""
            combined = f"{title} {text}".strip()[:1500]

            if combined:
                sentiment = get_sentiment(combined)
                topic = get_topic(combined)
                update_mention_analysis(mention_id, sentiment, topic)

            progress.progress(i / total)
            status.caption(f"Processed {i} / {total}")

        status.empty()
        progress.empty()

        st.success(f"✅ Analysis complete for {total} mention(s).")
        st.session_state.analysis_completed = True
        st.cache_data.clear()
        st.rerun()

# --------------------------------------------------------------
# Sidebar status badges (shown after rerun so state is current)
# --------------------------------------------------------------

with st.sidebar:
    if st.session_state.mentions_fetched:
        st.success(f"✔ {st.session_state.fetch_count} mentions fetched")
    if st.session_state.analysis_completed:
        st.success("✔ Analysis complete")

# ---------------------------------------------------------------------------
# Dashboard tabs — only render when analysis is done
# ---------------------------------------------------------------------------

charts_tab, details_tab = st.tabs(["📊 Charts", "🧾 Details"])

if not st.session_state.analysis_completed:
    with charts_tab:
        st.info("Complete the **Fetch → Analyse** steps in the sidebar to see charts.")
    with details_tab:
        st.info("Complete the **Fetch → Analyse** steps in the sidebar to see details.")

else:
    # -----------------------------------------------------------------------
    # Charts tab
    # -----------------------------------------------------------------------
    with charts_tab:

        col_pie, col_bar = st.columns(2)

        with col_pie:
            st.subheader("Sentiment")
            sentiment_data = get_sentiment_distribution(brand)

            if sentiment_data:
                df_s = pd.DataFrame(sentiment_data.items(), columns=["Sentiment", "Count"])
                COLOR_MAP = {"positive": "#22c55e", "neutral": "#6b7280", "negative": "#ef4444"}
                fig = px.pie(
                    df_s,
                    names="Sentiment",
                    values="Count",
                    color="Sentiment",
                    color_discrete_map=COLOR_MAP,
                    hole=0.45,
                )
                fig.update_traces(textposition="inside", textinfo="percent+label")
                fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sentiment data yet.")

        with col_bar:
            st.subheader("Topics")
            topic_data = get_topic_distribution(brand)

            if topic_data:
                df_t = pd.DataFrame(topic_data.items(), columns=["Topic", "Count"])
                df_t["Topic"] = df_t["Topic"].str.replace("_", " ").str.title()
                fig = px.bar(
                    df_t.sort_values("Count", ascending=True),
                    x="Count",
                    y="Topic",
                    orientation="h",
                    color="Count",
                    color_continuous_scale="Blues",
                )
                fig.update_layout(
                    coloraxis_showscale=False,
                    margin=dict(t=10, b=10, l=10, r=10),
                    yaxis_title=None,
                    xaxis_title="Mentions",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No topic data yet.")

        # Quick-glance metric row
        st.divider()
        mentions_all = get_mentions_table(brand)
        total = len(mentions_all)
        pos = sum(1 for m in mentions_all if m.get("sentiment") == "positive")
        neg = sum(1 for m in mentions_all if m.get("sentiment") == "negative")

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Mentions", total)
        m2.metric("Positive", pos, delta=None)
        m3.metric("Negative", neg, delta=None)

    # -----------------------------------------------------------------------
    # Details tab
    # -----------------------------------------------------------------------
    with details_tab:

        st.subheader("🧠 AI Summary")
        with st.spinner("Generating summary …"):
            summary = generate_brand_summary(brand)

        st.markdown(f"> {summary}" if summary else "_No summary available._")

        st.divider()
        st.subheader("📋 All Analysed Mentions")

        mentions = get_mentions_table(brand)
        if mentions:
            df = pd.DataFrame(mentions)

            # Clean up columns for display
            display_cols = ["timestamp", "title", "author", "sentiment", "topic", "score", "comments", "url"]
            df = df[[c for c in display_cols if c in df.columns]]
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")
            df["title"] = df["title"].str[:80]  # truncate long titles in table

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "url": st.column_config.LinkColumn("Link", display_text="Open ↗"),
                    "sentiment": st.column_config.TextColumn("Sentiment"),
                    "score": st.column_config.NumberColumn("Score", format="%d ⬆"),
                    "comments": st.column_config.NumberColumn("Comments", format="%d 💬"),
                },
            )
        else:
            st.info("No analysed mentions found.")