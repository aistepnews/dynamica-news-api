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
    # أولاً: نطلب من الفيتشِر أن يجلب أحدث الأخبار
    news_fetcher.fetch_news()
    # ثانياً: نقرأ من قاعدة البيانات بناءً على المعايير
    data = news_fetcher.get_news(limit=limit, processed=processed)
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail="Invalid data format")
    return data

@app.get("/narrative/{news_id}")
async def get_narrative(news_id: int):
    # نمرر العنوان والمحتوى للدالة المسؤولة عن التحليل
    narrative = generate_narrative(news_id)
    if not narrative:
        raise HTTPException(status_code=404, detail="Narrative not found.")
    return {"narrative": narrative}
