import sys
from pathlib import Path

# allow imports from src
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
# backend imports
from backend.database import (
    initialize_database,
    get_unanalyzed_mentions_by_brand,
    update_mention_analysis
)

from backend.data_sources import fetch_hackernews_mentions

from backend.ai_analysis import (
    get_sentiment,
    get_topic
)
# ----------------
# INITIAL TEMPLATE
# ----------------

# page configurations
st.set_page_config(
    page_title="AI Brand Monitor",
    page_icon="📊",
    layout="wide"
)

# app title
st.title("📊 AI Brand Monitoring Dashboard")

# short description
st.markdown(
"""
Monitor online discussions about a brand using AI.

This dashboard collects mentions from Hacker News,
analyzes sentiment and topics using an LLM, and
displays insights through charts and summaries.
"""
)


# -----------------
# SESSION STATE
# -----------------

# track if mentions were fetched 
if "mentions_fetched" not in st.session_state:
    st.session_state["mentions_fetched"] = False # enables AI analysis button

# track if analysis was completed
if "analysis_completed" not in st.session_state:
    st.session_state["analysis_completed"] = False # allows showing charts

# store mention count
if "mentions_count" not in st.session_state:
    st.session_state["mentions_count"] = 0 # display how many mentions fetched

# store current brand
if "current_brand" not in st.session_state:
    st.session_state["current_brand"] = "" # reset state when brand changes


# -----------------
# SIDEBAR CONTROLS
# -----------------

with st.sidebar:

    # title
    st.title("Brand Controls")

    # brand input
    brand = st.text_input(
        "Enter brand name",
        placeholder="e.g. OpenAI"
    )

    st.divider()

    # fetch mentions button
    fetch_button = st.button("Fetch Mentions")

    # run ai analysis button (enabled only after fetch)
    analyze_button = st.button(
        "Run AI Analysis",
        disabled=not st.session_state["mentions_fetched"]
    )

    st.divider()

    # instructions
    st.markdown(
    """
    ### Instructions
    1. Enter a brand name  
    2. Click **Fetch Mentions**  
    3. Click **Run AI Analysis**  
    4. View insights in the dashboard
    """
    )


# -----------------
# DASHBOARD TABS
# -----------------

# create tabs
charts_tab, details_tab = st.tabs(["📊 Charts", "🧾 Details"])


# charts tab
with charts_tab:

    st.subheader("Sentiment Distribution")

    # placeholder for pie chart
    st.info("Sentiment pie chart will appear here.")


    st.subheader("Topic Distribution")

    # placeholder for bar chart
    st.info("Topic bar chart will appear here.")


# details tab
with details_tab:

    st.subheader("AI Summary")

    # placeholder for summary
    st.info("AI-generated summary will appear here.")


    st.subheader("Mentions Table")

    # placeholder for mentions table
    st.info("Mentions table will appear here.")


# -----------------
# FETCH MENTIONS
# -----------------

if fetch_button:

    if not brand:
        st.warning("Please enter a brand name before fetching mentions.")

    else:

        initialize_database()

        with st.spinner("Fetching mentions from Hacker News..."):

            fetch_hackernews_mentions(brand)

        st.success("Mentions fetched successfully.")


# -----------------
# RUN AI ANALYSIS
# -----------------

if analyze_button:

    if not brand:
        st.warning("Please enter a brand name before running analysis.")

    else:

        mentions = get_unanalyzed_mentions_by_brand(brand)

        total_mentions = len(mentions)

        if total_mentions == 0:
            st.info("No new mentions to analyze.")
        else:

            st.write(f"Running AI analysis on {total_mentions} mentions...")

            progress_bar = st.progress(0)

            for i, mention in enumerate(mentions):

                mention_id = mention["id"]

                title = mention["title"] or ""
                text = mention["text"] or ""

                combined_text = f"{title} {text}".strip()[:1500]

                if not combined_text:
                    continue

                sentiment = get_sentiment(combined_text)
                topic = get_topic(combined_text)

                update_mention_analysis(
                    mention_id,
                    sentiment,
                    topic
                )

                progress = (i + 1) / total_mentions
                progress_bar.progress(progress)

            st.success("AI analysis completed.")