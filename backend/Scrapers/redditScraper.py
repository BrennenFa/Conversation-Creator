import praw
import os
from dotenv import load_dotenv
import json
from sentence_transformers import SentenceTransformer
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


load_dotenv()
REDDIT_ID=os.getenv("REDDIT_ID")
REDDIT_SECRET=os.getenv("REDDIT_SECRET")
REDDIT_USERNAME=os.getenv("REDDIT_USERNAME")


# STEP 1 -- ACCESS RELEVANT TRENDS
with open('../Trends/trends.json', 'r') as file:
    data = json.load(file)
trendingTopics = data["top_trends"]


# STEP 2 - generate the embeddings model and vector db
model = SentenceTransformer("all-MiniLM-L6-v2")

DB_DIR = Path("").resolve().as_posix()

os.makedirs(DB_DIR, exist_ok=True)

qdrant = QdrantClient(
    path=str(DB_DIR)
)
collection_name = "reddit_topics"

# create collection if it doesn't exist
if collection_name not in [c.name for c in qdrant.get_collections().collections]:
    qdrant.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )


# STEP 2 -- find elements related
reddit = praw.Reddit(
    client_id=f'{REDDIT_ID}',
    client_secret=f'{REDDIT_SECRET}',
    user_agent=f'trending_search_app by /u/{REDDIT_USERNAME}'
)




# Search across all subreddits
for idx, topic in enumerate(trendingTopics):
    posts = reddit.subreddit("all").search(topic, sort="relevance", time_filter="day", limit=10)
    text = f"Topic: {topic}\n\n"
    postMetadata = []
    for post in posts:
        text += f"Title: {post.title}\n{post.selftext}\n"
        for comment in post.comments[:10]:
            text += f"- {comment.body}\n"
        text += "\n"
        postMetadata.append({
            "title": post.title,
            "selftext": post.selftext,
            "comments": comment.body
        })

    embedding = model.encode(text)

    qdrant.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=idx,  # You can also use UUIDs
                vector=embedding,
                payload={
                    "topic": topic,
                    "text": text,
                    "metadata": postMetadata
                }
            )
        ]
    )
    print(f"Inserted topic: {topic}")


    


