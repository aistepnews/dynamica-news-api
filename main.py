from fastapi import FastAPI, HTTPException
from news_fetcher_service import NewsService
from narrative_generator import generate_narrative
from news_fetcher import NewsAutoFetcher

app = FastAPI()
news_service = NewsService()
news_fetcher = NewsAutoFetcher()

@app.get("/")
async def root():
    return {"message": "Welcome to Dynamica News API!"}

@app.get("/news")
async def get_news_list():
    try:
        news_data = news_fetcher.get_news()
        if not news_data:
            raise HTTPException(status_code=404, detail="No news found.")
        return news_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/narrative/{news_id}")
async def get_narrative(news_id: int):
    try:
        narrative = generate_narrative(news_id)
        if not narrative:
            raise HTTPException(status_code=404, detail="Narrative not found.")
        return narrative
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
