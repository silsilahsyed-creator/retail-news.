"""Fetches Indian retail news from NewsData.io and saves it to news.json."""
import json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

API_KEY = os.environ.get("NEWSDATA_API_KEY")
if not API_KEY:
    sys.exit("Missing NEWSDATA_API_KEY")

# Each topic becomes a category tab on the site. Queries must stay under 100 characters.
TOPICS = {
    "Retail": 'retail OR retailer OR "retail chain" OR "store expansion"',
    "E-commerce": "ecommerce OR Flipkart OR Amazon OR Meesho",
    "Quick commerce": '"quick commerce" OR Blinkit OR Zepto OR Instamart',
    "Fashion": '"fashion retail" OR Myntra OR Nykaa OR Ajio',
    "Grocery": 'DMart OR BigBasket OR "Reliance Retail" OR grocery',
}
MAX_ARTICLES = 300
FILE = "news.json"

def fetch(query):
    params = urllib.parse.urlencode(
        {"apikey": API_KEY, "q": query, "country": "in", "language": "en"}
    )
    url = "https://newsdata.io/api/1/latest?" + params
    with urllib.request.urlopen(url, timeout=30) as r:
        data = json.load(r)
    return data.get("results") or []

try:
    with open(FILE, encoding="utf-8") as f:
        old = json.load(f).get("articles", [])
except Exception:
    old = []

by_link = {a["link"]: a for a in old}
for category, query in TOPICS.items():
    try:
        results = fetch(query)
    except Exception as e:
        print(f"Skipped {category}: {e}")
        continue
    for item in results:
        link = item.get("link")
        title = (item.get("title") or "").strip()
        if not link or not title or link in by_link:
            continue
        by_link[link] = {
            "title": title,
            "summary": (item.get("description") or "").strip()[:240],
            "link": link,
            "image": item.get("image_url") or "",
            "source": item.get("source_name") or item.get("source_id") or "",
            "date": item.get("pubDate") or "",
            "category": category,
        }

articles = sorted(by_link.values(), key=lambda a: a["date"], reverse=True)[:MAX_ARTICLES]
with open(FILE, "w", encoding="utf-8") as f:
    json.dump(
        {"updated": datetime.now(timezone.utc).isoformat(), "articles": articles},
        f, ensure_ascii=False, indent=1,
    )
print(f"Saved {len(articles)} articles")
