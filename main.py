from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from news_fetcher import NewsAutoFetcher
from narrative_generator import generate_narrative

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

news_fetcher = NewsAutoFetcher()

@app.get("/")
async def root():
    return {"message": "Welcome to Dynamica News API!"}

@app.get("/news")
async def get_news_list(limit: int = 10, processed: bool = False):
    news_fetcher.fetch_news()
    data = news_fetcher.get_news(limit=limit, processed=processed)
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="Invalid data format")
    return data

@app.get("/narrative/{news_id}")
async def get_narrative(news_id: int):
    # جلب كل الأخبار ثم البحث عن الخبر المطلوب
    all_news = news_fetcher.get_news(limit=1000)
    item = next((n for n in all_news if n["id"] == news_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="خبر غير موجود.")
    # توليد الرواية بناءً على العنوان والمحتوى
    narrative = generate_narrative(item["title"], item["content"])
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found.")
    return {"narrative": narrative}
