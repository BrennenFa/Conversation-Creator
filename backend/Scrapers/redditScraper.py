import praw
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from datetime import datetime
import uuid

# Currently inactive
# whoops

load_dotenv()
REDDIT_ID=os.getenv("REDDIT_ID")
REDDIT_SECRET=os.getenv("REDDIT_SECRET")
REDDIT_USERNAME=os.getenv("REDDIT_USERNAME")


# init reddit api
reddit = praw.Reddit(
    client_id=REDDIT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=f'trending_search_app by /u/{REDDIT_USERNAME}'
)


# List of subreddits to check
subreddits = [
    "news",
    "worldnews",
    "technology",
    "science",
    "politics",
    "sports",
]

# Initialize sentence model and Chroma
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="../chroma_db")
collection = client.get_or_create_collection(
    name="reddit",
    metadata={"hnsw:space": "cosine"}
)


# iteratae through each subreddit
for subbreddit in subreddits:
    print(f"r/{subbreddit}")
    subreddit = reddit.subreddit(subbreddit)

    # first 5 hot posts
    for post in subreddit.hot(limit=5):
        text = f"Subreddit: r/{subbreddit}\n"
        text += f"Title: {post.title}\n"
        text += f"Content: {post.selftext}\n\n"
        text += "Comments:\n"

        # first 5 comments
        numComments = 0
        for comment in post.comments[:5]:
            try:
                if hasattr(comment, 'body'):
                    text += f"- {comment.body}\n"
                    numComments += 1
            except:
                pass

        # Create embedding and store
        embedding = model.encode(text).tolist()

        collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[str(uuid.uuid4())],
            metadatas=[{
                "subreddit": subbreddit,
                "post_title": post.title,
                "source": "reddit",
                "scraped_at": datetime.now().timestamp(),
                "number_comments": numComments
            }]
        )

    print()

print(f"Items in collection: {collection.count()}")



