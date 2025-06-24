import requests
from bs4 import BeautifulSoup
import tweepy
import os
from dotenv import load_dotenv

# use if i need to use webscraping
# import asyncio
# from playwright.async_api import async_playwright




url = "https://trends24.in/united-states/"


# find website with top tweets 
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



load_dotenv()
bearer_token = os.getenv("BEARER_TOKEN")
client = tweepy.Client(bearer_token=bearer_token)
print(bearer_token)
# Find corresponding tweets
print("Top Twitter Trends (Global):\n")
tweets = {}


for i, tag in enumerate(trendingTags[:10], 1):
    tagTweets = []
    # tag = tag[1:]
    print(f"{i}. {tag}")
    query = f"{tag} lang:en"
    response = client.search_recent_tweets(query=query, max_results=1)

    for i, tweet in enumerate(response.data, 1):
        print(f"{i}. {tweet.text}")



    
    tweets[tag] = tagTweets
    print(tagTweets)


