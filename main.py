from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from news_fetcher import NewsAutoFetcher
from narrative_generator import generate_narrative

app = FastAPI()

# تفعيل CORS لأي دومين (للوحة الأمامية)
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
    # أولاً: جلب جديد الأخبار من المصادر
    news_fetcher.fetch_news()
    # ثانياً: قراءة الأخبار من قاعدة البيانات
    data = news_fetcher.get_news(limit=limit, processed=processed)
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="Invalid data format")
    return data

@app.get("/narrative/{news_id}")
async def get_narrative(news_id: int):
    # نقرأ الخبر من قاعدة البيانات حسب الـ id
    item = news_fetcher.get_news_by_id(news_id)
    if not item:
        raise HTTPException(status_code=404, detail="خبر غير موجود.")
    # نمرّر العنوان والمحتوى لدالة التحليل
    analysis = generate_narrative(item["title"], item["content"])
    if not analysis:
        raise HTTPException(status_code=500, detail="فشل تحليل الخبر.")
    # نضعه مُعالج في القاعدة (اختياري)
    news_fetcher.mark_as_processed(news_id)
    return {"id": news_id, "narrative": analysis}
