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
    # نجمع الأخبار (من RSS) ثم نرجّع أول X عناصر
    news_fetcher.fetch_news()
    data = news_fetcher.get_news(limit=limit, processed=processed)
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="Invalid data format")
    return data

@app.get("/narrative/{news_id}")
async def get_narrative(news_id: int):
    # أولًا نحصل على الخبر من قاعدة البيانات
    all_news = news_fetcher.get_news(limit=1000)  # نجلب كل الأخبار
    item = next((n for n in all_news if n["id"] == news_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="خبر غير موجود.")
    # نبني النص ونمرره لدالة التحليل
    analysis = generate_narrative(item["title"], item["content"])
    return {"narrative": analysis}
