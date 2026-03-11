import requests

# -------------------------------------------------
# get latest story ids
# -------------------------------------------------

url = "https://hacker-news.firebaseio.com/v0/newstories.json"

ids = requests.get(url).json()

print("Latest story IDs:")
print(ids[:10])  # preview first few


# -------------------------------------------------
# fetch a single STORY using story_id
# -------------------------------------------------

story_id = ids[0]

item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"

response = requests.get(item_url)

if response.status_code == 200:

    story = response.json()

    print(story)

    print("\nFetched Story:\n")

    print("ID:", story.get("id"))
    print("Type:", story.get("type"))
    print("Author:", story.get("by"))
    print("Title:", story.get("title"))
    print("Text:", story.get("text"))
    print("URL:", story.get("url"))
    print("Time:", story.get("time"))
    print("Comment IDs:", story.get("kids"))

else:
    print("Failed to fetch story")


# Latest story IDs:
# [47284781, 47284778, 47284766, 47284763, 47284752, 47284748, 47284742, 47284719, 47284701, 47284699]

# Fetched Story:

# ID: 47284781
# Type: story
# Author: luu
# Title: How many options fit into a boolean?
# Text: None
# URL: https://herecomesthemoon.net/2025/11/how-many-options-fit-into-a-boolean/
# Time: 1772861473
# Comment IDs: None