'''
This module is responsible for helping UI components:
----
Reflect Table (mentions table)
Pie Chart (sentiment)
Bar Chart (topic)
AI insights (brand summary)
'''
import sqlite3
from langchain_ollama import ChatOllama
from backend.config import DatabaseConfig, LLMConfig
import streamlit as st # for caching eg. charts data etc, 
# so ui does not reload on every streamlit auto rerun, when inputs are same


# For Table display in UI
@st.cache_data
def get_mentions_table(brand):
    """
    Retrieve analyzed mentions for a given brand.

    Workflow
    --------
    1. Open database connection
    2. Fetch analyzed mentions for the brand
    3. Order mentions by latest timestamp
    4. Convert rows to dictionary format
    5. Return mentions list
    """

    # build connection
    with sqlite3.connect(database=DatabaseConfig.DB_PATH) as conn:

        # makes rows accessible by column name (originally row data is in tuple form)
        conn.row_factory = sqlite3.Row

        # build cursor
        cursor = conn.cursor()

        # build command
        command = """
        SELECT *
        FROM mentions
        WHERE brand = ?
        AND sentiment IS NOT NULL
        ORDER BY timestamp DESC
        """

        # execute command
        cursor.execute(command, (brand,))

        # saving not required as just reading

        # fetch rows
        rows = cursor.fetchall()

        # convert rows to dictionaries
        mentions = [dict(row) for row in rows]

        # and with.. will close connection automatically

        return mentions
    

# eg.
# get_sentiment_distribution("OpenAI")
# - query database
# - cache result

# next time.
# get_sentiment_distribution("OpenAI")
# - return cached result instantly
# (no DB query)

@st.cache_data
def get_sentiment_distribution(brand):
    """
    Retrieve sentiment counts for a given brand.

    Workflow
    --------
    1. Open database connection
    2. Count mentions grouped by sentiment
    3. Fetch aggregated results
    4. Convert results to dictionary format
    5. Return sentiment distribution
    """

    # build connection
    with sqlite3.connect(database=DatabaseConfig.DB_PATH) as conn:

        # build cursor
        cursor = conn.cursor()

        # build command
        command = """
        SELECT sentiment, COUNT(*) as count
        FROM mentions
        WHERE brand = ?
        AND sentiment IS NOT NULL
        GROUP BY sentiment
        """

        # execute command
        cursor.execute(command, (brand,))

        # fetch rows
        rows = cursor.fetchall()

        # convert results into dictionary
        sentiment_distribution = {
            sentiment: count for sentiment, count in rows
        }

        # eg. rows:
        # rows = [
        #     ("positive", 12),
        #     ("neutral", 7),
        #     ("negative", 5)
        # ]

        # they are in structure (why only sentiment and count? -> sql we filtered already)
        # => (sentiment, count)

        # then we create dict entry:
        # {
        # "positive": 12,
        # "neutral": 7,
        # "negative": 5
        # }

        return sentiment_distribution
    

@st.cache_data
def get_topic_distribution(brand):
    """
    Retrieve topic counts for a given brand.

    Workflow
    --------
    1. Open database connection
    2. Count mentions grouped by topic
    3. Fetch aggregated results
    4. Convert results to dictionary format
    5. Return topic distribution
    """

    # build connection
    with sqlite3.connect(database=DatabaseConfig.DB_PATH) as conn:

        # build cursor
        cursor = conn.cursor()

        # build command
        command = """
        SELECT topic, COUNT(*) as count
        FROM mentions
        WHERE brand = ?
        AND topic IS NOT NULL
        GROUP BY topic
        """

        # execute command
        cursor.execute(command, (brand,))

        # fetch rows
        rows = cursor.fetchall()

        # convert results into dictionary
        topic_distribution = {
            topic: count for topic, count in rows
        }
        # eg. rows:
        # rows = [
        #     ("pricing", 6),
        #     ("product_feedback", 8),
        #     ("feature_request", 4),
        #     ("bug_report", 3)
        #         ]

        # they are in structure (why only topic and count? -> sql we filtered already)
        # => (topic, count)

        # then we create dict entry:
        # {
        # "pricing": 6,
        # "product_feedback": 8,
        # "feature_request": 4,
        # "bug_report": 3
        # }

        return topic_distribution


@st.cache_data
def generate_brand_summary(brand):
    """
    Generate AI summary of brand discussions.

    Workflow
    --------
    1. Open database connection
    2. Retrieve analyzed mentions for the brand
    3. Combine mention texts for context
    4. Send context to LLM for summarization
    5. Return generated summary
    """

    # build connection
    with sqlite3.connect(database=DatabaseConfig.DB_PATH) as conn:

        # build cursor
        cursor = conn.cursor()

        # build command
        command = """
        SELECT title, text, sentiment, topic
        FROM mentions
        WHERE brand = ?
        AND sentiment IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 20
        """

        # execute command
        cursor.execute(command, (brand,))

        # fetch rows
        rows = cursor.fetchall()

    # build text context
    context = ""

    for title, text, sentiment, topic in rows:

        title = title or ""
        text = text or ""

        context += f"""
        Title: {title}
        Text: {text}
        Sentiment: {sentiment}
        Topic: {topic}
        """

    # initialize model
    model = ChatOllama(model=LLMConfig.LLM_MODEL)

    prompt = f"""
    You are a brand monitoring analyst.

    Analyze the following discussions about the brand "{brand}"
    and generate a concise summary of the overall sentiment
    and key topics being discussed.

    Rules:
    - Write 2-3 sentences only
    - Focus on major trends
    - Do not list individual posts

    Discussions:
    {context}
    """

    try:
        response = model.invoke(prompt)

        summary = response.content.strip()

        return summary

    except Exception as e:
        print(f"Summary generation error: {e}")
        return "Summary could not be generated."