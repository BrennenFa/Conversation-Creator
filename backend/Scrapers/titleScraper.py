import requests
from bs4 import BeautifulSoup
import tweepy
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from datetime import datetime
import uuid


url = "https://trends24.in/united-states/"
headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)

# webscrape top tweets
soup = BeautifulSoup(response.text, 'html.parser')
trendingTags = []

tagsWeb = soup.find_all("a", class_="trend-link")
for topics in tagsWeb:
        tag = topics.get_text(strip=True)
        trendingTags.append(tag)


# init chromadb
model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="../chroma_db")
collection = chroma_client.get_or_create_collection(
    name="titles",
    metadata={"hnsw:space": "cosine"}
)

NUM_TAGS = 100
# store trending tags in db
for i, tag in enumerate(trendingTags[:NUM_TAGS], 1):
    clean_tag = tag[1:] if tag and tag[0] in ['$', '#'] else tag

    text = f"Trending Topic: {clean_tag}"
    embedding = model.encode(text).tolist()

    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[str(uuid.uuid4())],
        metadatas=[{
            "topic": clean_tag,
            "original_tag": tag,
            "source": "trends24",
            "scraped_at": datetime.now().isoformat(),
            "rank": i
        }]
    )

print(f"\nTrending tags scraping complete")
print(f"Collection size: {collection.count()}")
