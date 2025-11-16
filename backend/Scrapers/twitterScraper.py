import requests
from bs4 import BeautifulSoup
import tweepy
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from datetime import datetime
import uuid

# load env variables
load_dotenv()
bearer_token = os.getenv("BEARER_TOKEN")
twitter_client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)



# top tweets 
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
        if len(trendingTags) >= 20:
            break

print(trendingTags)



# init chromadb
model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="../chroma_db")
collection = chroma_client.get_or_create_collection(
    name="twitter",
    metadata={"hnsw:space": "cosine"}
)

# N topics × M tweets = (n * m) tweets/day
# (50 tweet/day limit) w/ free tier
NUM_TOPICS = 1
# minimum allowed by Twitter API
TWEETS_PER_TOPIC = 10

# iterate throgh trending tags
for i, tag in enumerate(trendingTags[:NUM_TOPICS], 1):
    clean_tag = tag[1:] if tag[0] in ['$', '#'] else tag
    print(f"{i}. {clean_tag}")

    query = f"{clean_tag} lang:en"
    response = twitter_client.search_recent_tweets(query=query, max_results=TWEETS_PER_TOPIC)

    if response.data:
        # combine all tweets for tag
        tweetText = f"Topic: {clean_tag}\n\n"
        tweetText += "\n".join([f"- {tweet.text}" for tweet in response.data])

        # Generate embedding
        embedding = model.encode(tweetText).tolist()

        # add to chroma
        collection.add(
            documents=[tweetText],
            embeddings=[embedding],
            ids=[str(uuid.uuid4())],
            metadatas=[{
                "topic": clean_tag,
                "source": "twitter",
                "scraped_at": datetime.now().isoformat(),
                "tweet_count": len(response.data)
            }]
        )
        print(f"Inserted {len(response.data)} tweets for: {clean_tag}")
    else:
        print(f"No tweets found for: {clean_tag}")

print(f"\nTwitter scraping complete")
print(f"Collection size: {collection.count()}")
