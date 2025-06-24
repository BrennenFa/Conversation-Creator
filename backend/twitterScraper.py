import requests
from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright
# import ssl
import os
from dotenv import load_dotenv
load_dotenv()

EMAIL = os.getenv("TWITTER_EMAIL")
PASSWORD = os.getenv("TWITTER_PASSWORD")



url = "https://trends24.in/united-states/"


# playwright webscraping
async def twitterData(tag):
    url = f"https://twitter.com/search?q={tag}&src=trend_click&f=top"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_timeout(5000)

        tweet_elements = await page.locator('article').all_inner_texts()
        await browser.close()

    # return tweets
    return tweet_elements[:5]



import certifi
print(certifi.where())
response = requests.get("https://twitter.com", verify=certifi.where())
print(response.status_code)
headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)

# parse the website to find trending tags
soup = BeautifulSoup(response.text, 'html.parser')

trendingTags = []

# Find the trends
hashtags = soup.find_all("a", class_="trend-link")

for hashtag in hashtags:
        tag = hashtag.get_text(strip=True)
        trendingTags.append(tag)


print("Top Twitter Trends (Global):\n")
tweets = {}

# top 10 twitter trends
for i, tag in enumerate(trendingTags[:10], 1):
    tagTweets = []
    # tag = tag[1:]
    print(f"{i}. {tag}")

    tagTweets = asyncio.run(twitterData(tag))
    for j, tweet in enumerate(tagTweets):
         print(tweet)



    
    tweets[tag] = tagTweets
    print(tagTweets)


