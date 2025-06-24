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
    query = tag.replace(" ", "%20")
    url = f"https://twitter.com/search?q={query}&src=typed_query&f=live"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        # close any popup
        context.on("page", lambda popup: asyncio.create_task(popup.close()))

        page = await context.new_page()
        await page.goto("https://twitter.com/login")
        await page.fill('input[name="text"]', EMAIL)
        # await page.press('input[name="text"]', 'Enter')


        # try to find buttongs
        # buttons = await page.locator('div[role="button"]').all()
        # for i, btn in enumerate(buttons):
        #     text = await btn.inner_text()
        #     print(f"{i}: {text}")

        await page.locator('div[role="button"]:has-text("Next")').wait_for(state='visible')
        print("visible")
        await page.locator('div[role="button"]:has-text("Next")').click()

        await page.fill('input[name="password"]', PASSWORD)
        await page.click('div[data-testid="LoginForm_Login_Button"]')

        await page.wait_for_load_state("networkidle")

        # first 10 tweens
        await page.goto(url)

        await page.wait_for_selector("article")

        tweets = await page.locator("article").all()
        for i, tweet in enumerate(tweets[:10], 1):
            try:
                content = await tweet.inner_text()
                print(f"{i}. {content[:200]}")
            except Exception as e:
                print(f"{i}. Error: {e}")
        
        await browser.close()
    # return tweets



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


