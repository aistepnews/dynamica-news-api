from fastapi import FastAPI
from news_fetcher_service import get_news
from narrative_generator import generate_narrative

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to Dynamica News API!"}

@app.get("/news")
async def get_news_list():
    # جلب الأخبار من خدمة الأخبار
    news_data = get_news()
    return news_data

@app.get("/narrative/{news_id}")
async def get_narrative(news_id: int):
    # تحليل الخبر باستخدام الذكاء الاصطناعي
    narrative = generate_narrative(news_id)
    return narrative
