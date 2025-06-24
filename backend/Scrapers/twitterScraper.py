import requests
from bs4 import BeautifulSoup
import tweepy
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
# use if i need to use webscraping
# import asyncio
# from playwright.async_api import async_playwright

# load env variables
load_dotenv()
bearer_token = os.getenv("BEARER_TOKEN")
client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)



# find website with top tweets 

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




# Find corresponding tweets
print("Top Twitter Trends (Global):\n")

allTweets = []
# for testing purposes
tweetDict = {}


for i, tag in enumerate(trendingTags[:5], 1):
    tagTweets = []
    if tag[0] == '$' or tag[0] == '#':
        tag = tag[1:]
    print(f"{i}. {tag}")
    query = f"{tag} lang:en"
    response = client.search_recent_tweets(query=query, max_results=10)

    for i, tweet in enumerate(response.data, 1):
        print(f"{i}. {tweet.text}")
        tagTweets.append(tweet.text)
        allTweets.append(tweet.text)

    tweetDict[tag] = tagTweets


# upload to a vectgor databse
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(allTweets)

client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",
                                    persist_directory="db/"
                                ))
collection = client.create_or_get_collection(name="content")

for i, text in enumerate(allTweets):
    collection.add(documents=[text], embeddings=[embeddings[i]], ids=[f"tweet_{i}"])

