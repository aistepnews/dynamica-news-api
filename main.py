from fastapi import FastAPI, HTTPException
from news_fetcher_service import get_news  # تأكد من أن هذه الدالة موجودة
from narrative_generator import generate_narrative  # تأكد من أن هذه الدالة موجودة

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to Dynamica News API!"}

@app.get("/news")
async def get_news_list():
    try:
        # جلب الأخبار من خدمة الأخبار
        news_data = get_news()
        if not news_data:
            raise HTTPException(status_code=404, detail="No news found.")
        return news_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/narrative/{news_id}")
async def get_narrative(news_id: int):
    try:
        # تحليل الخبر باستخدام الذكاء الاصطناعي
        narrative = generate_narrative(news_id)
        if not narrative:
            raise HTTPException(status_code=404, detail="Narrative not found for the given news_id.")
        return narrative
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
