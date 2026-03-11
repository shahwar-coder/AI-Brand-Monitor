'''
This module is responsible for collecting raw data from external platforms.
'''
import requests
from datetime import datetime
from backend.config import APIConfig
from backend.database import insert_mention


def fetch_hackernews_mentions(brand):
    """
    Fetch the latest story IDs from the Hacker News API.
    For each story ID:
        - Retrieve story details from the API.
        - Skip if the story is invalid or not a "story" type.
        - Check whether the brand appears in the title or text.
        - Extract relevant fields (title, text, url, author, score, comments, timestamp).
        - Insert the mention into the database.
    """

    url = f"{APIConfig.HN_API_BASE}/newstories.json"

    try:
        response = requests.get(url=url)
        response.raise_for_status()
        story_ids = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching story IDs: {e}")
        return 0

    # we will process limited no:of stories
    story_ids = story_ids[:50]

    mentions_added = 0

    for story_id in story_ids:

        item_url = f"{APIConfig.HN_API_BASE}/item/{story_id}.json"

        try:
            response = requests.get(url=item_url)
            response.raise_for_status()
            story = response.json()
        except requests.exceptions.RequestException:
            continue

        # sometime story = None
        if not story:
            continue

        # skip non-story items
        if story.get("type") != "story":
            continue

        # transform data according to our schema
        # id -> auto increment
        # brand -> come from user input

        source = "hackernews"

        title = story.get("title", "")
        text = story.get("text", "")

        # skip empty content
        if not title and not text:
            continue

        # check brand mention
        combined_text = f"{title} {text}"
        if brand.lower() not in combined_text.lower():
            continue

        fallback_url = f"https://news.ycombinator.com/item?id={story_id}"
        url = story.get("url", fallback_url)

        author = story.get("by", "")
        score = story.get("score", 0)
        comments = story.get("descendants", 0)

        time_value = story.get("time")

        if time_value:
            timestamp = datetime.fromtimestamp(time_value)
        else:
            timestamp = None

        insert_mention(
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

        mentions_added += 1

    return mentions_added


# example for both APIs:
# newstories API -> [47284781, 47284778, 47284766, 47284763,...
# each story API -> data = {
#     "by": "semtex_cz",
#     "descendants": 0,
#     "id": 47295683,
#     "score": 1,
#     "text": "...",
#     "time": 1772959537,
#     "title": "Show HN: Bookvoice – convert PDF books into audiobooks",
#     "type": "story",
#     "url": "https://github.com/Semtexcz/Bookvoice"
# }