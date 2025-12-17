import requests
from bs4 import BeautifulSoup
import time
import os

BASE_URL = "https://techcrunch.com/latest/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

FILE_NAME = "techcrunch_articles.txt"

# ------------------------------------------------
# STEP 1: Load existing titles (to avoid duplicates)
# ------------------------------------------------
existing_titles = set()

if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
                existing_titles.add(title)

print(f"Loaded {len(existing_titles)} existing titles")

# ------------------------------------------------
# STEP 2: Get latest articles page
# ------------------------------------------------
response = requests.get(BASE_URL, headers=HEADERS)
soup = BeautifulSoup(response.text, "lxml")

headlines = soup.find_all("h3")
article_links = []

for h in headlines:
    a_tag = h.find("a")
    if a_tag and "href" in a_tag.attrs:
        link = a_tag["href"]
        if link.startswith("https://techcrunch.com"):
            article_links.append(link)

# ------------------------------------------------
# STEP 3: Scrape each article
# ------------------------------------------------
with open(FILE_NAME, "a", encoding="utf-8") as file:

    for link in article_links[:5]:  # safe limit
        print(f"Checking: {link}")

        article_response = requests.get(link, headers=HEADERS)
        article_soup = BeautifulSoup(article_response.text, "lxml")

        # Title
        title_tag = article_soup.find("h1")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)

        # ❌ Skip duplicates
        if title in existing_titles:
            print("Duplicate found, skipping")
            continue

        # Author
        author_tag = article_soup.find("a", rel="author")
        author = author_tag.get_text(strip=True) if author_tag else "Unknown Author"

        # Date
        date_tag = article_soup.find("time")
        date = date_tag.get_text(strip=True) if date_tag else "No Date"

        # Content
        paragraphs = article_soup.find_all("p")
        content = []

        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50:
                content.append(text)

        # Save NEW article
        file.write("=" * 80 + "\n")
        file.write(f"Title: {title}\n")
        file.write(f"Author: {author}\n")
        file.write(f"Date: {date}\n")
        file.write(f"Link: {link}\n\n")

        for para in content:
            file.write(para + "\n\n")

        existing_titles.add(title)
        print("New article saved ✅")

        time.sleep(2)  # respect the site

print("Done. File updated.")
