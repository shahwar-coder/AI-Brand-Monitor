"""
This module handles AI-based analysis of brand mentions.

Responsibilities:
---------------
1. Sentiment classification
2. Topic classification
3. Running AI analysis on new mentions and updating the database
"""

from langchain_ollama import ChatOllama
from backend.config import LLMConfig
from backend.database import (
    get_unanalyzed_mentions_by_brand,
    update_mention_analysis
)

# initialize model
model = ChatOllama(model=LLMConfig.LLM_MODEL)


def get_sentiment(text):
    """
    Classify the sentiment of a given text.

    Returns one of:
    positive, negative, neutral
    """

    prompt = f"""
    You are a sentiment analysis classifier.

    Task:
    Determine the sentiment of the provided text.

    Rules:
    - Respond with ONLY one word.
    - Allowed answers: positive, negative, neutral
    - Do not explain.

    Text:
    {text}
    """

    try:
        response = model.invoke(prompt)

        sentiment = response.content.strip().lower()

        if sentiment not in {"positive", "negative", "neutral"}:
            return "neutral"

        return sentiment

    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return "neutral"
    

def get_topic(text):
    """
    Classify the topic of a given text.

    Returns one of:
    product_feedback, bug_report, pricing, feature_request, general_discussion
    """

    prompt = f"""
    You are a topic classification system.

    Task:
    Determine the main topic of the provided text.

    Rules:
    - Respond with ONLY one category.
    - Allowed answers: product_feedback, bug_report, pricing, feature_request, general_discussion
    - Do not explain.

    Text:
    {text}
    """

    try:
        response = model.invoke(prompt)

        topic = response.content.strip().lower()

        if topic not in {
            "product_feedback",
            "bug_report",
            "pricing",
            "feature_request",
            "general_discussion"
        }:
            return "general_discussion"

        return topic

    except Exception as e:
        print(f"Topic classification error: {e}")
        return "general_discussion"


def analyze_mentions_for_brand(brand):
    """
    Retrieve mentions for the brand from DB
    for each mention
        extract title & text
        combine title & text
        run sentiment classification
        run topic classification
        update DB row
    """

    mentions = get_unanalyzed_mentions_by_brand(brand)
    # NOTE : The filtering is removed from Python and put in SQL using `AND sentiment IS NULL` in SQL command

    for mention in mentions:

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
