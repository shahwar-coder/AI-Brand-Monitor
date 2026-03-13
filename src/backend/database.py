import sqlite3
from backend.config import DatabaseConfig

'''
This module is responsible for DB interactions
All functions that will interact with db:

initialize_database()
insert_mention()
get_unanalyzed_mentions_by_brand()
update_mention_analysis()
'''

def initialize_database():
    """
    Initialize database with Brand Mentions Table
    """
    # build a connection (for interaction with db)
    with sqlite3.connect(database=DatabaseConfig.DB_PATH) as conn:

        # build cursor (to execute sql commands)
        cursor = conn.cursor()

        # command to be executed
        command = """
        CREATE TABLE IF NOT EXISTS mentions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            source TEXT NOT NULL,
            title TEXT,
            text TEXT,
            url TEXT UNIQUE,
            author TEXT,
            score INTEGER,
            comments INTEGER,
            timestamp DATETIME,
            sentiment TEXT,
            topic TEXT
        )
        """

        # use the cursor to execute the command
        cursor.execute(command)

        # commit the changes (for permanent saving, not just in-memory)
        conn.commit()

        # close the connection might not be required if using `with`
        # conn.close()


def insert_mention(
    brand,
    source,
    title,
    text,
    url,
    author,
    score,
    comments,
    timestamp
):
    """
    Insert a new mention into mentions table
    """
    # build a connection
    with sqlite3.connect(database=DatabaseConfig.DB_PATH) as conn:

        # build cursor
        cursor = conn.cursor()

        # command (insert mention)
        command = """
        INSERT OR IGNORE INTO mentions (
            brand,
            source,
            title,
            text,
            url,
            author,
            score,
            comments,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # execute the command
        cursor.execute(
            command,
            (
                brand,
                source,
                title,
                text,
                url,
                author,
                score,
                comments,
                timestamp
            )
        )

        # save changes (persistance)
        conn.commit()


def get_unanalyzed_mentions_by_brand(brand):
    """
    Get mentions by brand

    Open database connection
    Execute SELECT query for the brand
    Fetch matching rows
    Convert rows to dictionary format (easy to extract later)
    Return list of mentions
    """
    # build connection
    with sqlite3.connect(database=DatabaseConfig.DB_PATH) as conn:

        # Makes rows accessible by column name, e.g. mention["id"]
        conn.row_factory = sqlite3.Row

        # build cursor
        cursor = conn.cursor()

        # build command
        command = """
        SELECT *
        FROM mentions
        WHERE brand = ?
        AND sentiment IS NULL
        ORDER BY timestamp DESC
        """

        # execute the command
        cursor.execute(command, (brand,))

        # fetch results and convert to plain dicts so they survive outside `with`
        results = [dict(row) for row in cursor.fetchall()]

        return results
    

def update_mention_analysis(mention_id, sentiment, topic):
    """
    Update mention with AI analysis results
    """
    # build connection
    with sqlite3.connect(database=DatabaseConfig.DB_PATH) as conn:

        # build cursor
        cursor = conn.cursor()

        # build command
        command = """
        UPDATE mentions
        SET sentiment = ?, topic = ?
        WHERE id = ?
        """

        # execute the command
        cursor.execute(
            command,
            (sentiment, topic, mention_id)
        )

        # save changes (persistence)
        conn.commit()

        # later it will be used like:
        # sentiment = get_sentiment(text)
        # topic = get_topic(text)

        # update_mention_analysis(
        #     mention_id,
        #     sentiment,
        #     topic,
        # )
        # NOTE: This basically completes the row with 2 analysis col values