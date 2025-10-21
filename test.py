import requests
from bs4 import BeautifulSoup

# URL of the WSJ tech page
url = "https://www.wsj.com/tech?mod=nav_top_section"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0"
}

# Fetch the page
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Find all articles
articles = soup.find_all("div", {"data-testid": "tech-front-article"})

# Get first 3
for article in articles[:3]:
    headline_tag = article.find("h3")
    link_tag = article.find("a", {"data-testid": "flexcard-headline"})
    
    if headline_tag and link_tag:
        title = headline_tag.get_text(strip=True)
        link = link_tag['href']
        print(f"Title: {title}")
        print(f"Link: {link}")
        print("-" * 50)
