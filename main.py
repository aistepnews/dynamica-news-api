from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import feedparser
from datetime import datetime

app = FastAPI()

# إعدادات CORS
origins = [
    "https://aistepnews.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# روابط RSS Feeds للمصادر الثلاثة
RSS_FEEDS = [
    "https://stepagency-sy.net/feed/",
    "https://www.aljazeera.net/aljazeerarss",
    "https://www.syria.tv/rss.xml"
]

def fetch_all_news():
    news_items = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            news_items.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published if "published" in entry else datetime.now().isoformat(),
                "summary": entry.summary if "summary" in entry else "",
                "source": feed.feed.title if "title" in feed.feed else "Unknown",
            })
    # ترتيب الأخبار من الأحدث إلى الأقدم (اختياري)
    news_items.sort(key=lambda x: x['published'], reverse=True)
    return news_items

@app.get("/")
def read_root():
    return {"message": "أهلاً بكم في وكالة دايناميكا الإخبارية!"}

@app.get("/news")
def get_news():
    news = fetch_all_news()
    return news
