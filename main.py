from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from news_fetcher import NewsAutoFetcher
from narrative_generator import generate_narrative

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aistepnews.github.io",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

news_fetcher = NewsAutoFetcher()

@app.get("/")
async def root():
    return {"message": "Welcome to Dynamica News API!"}

@app.get("/news")
async def get_news_list():
    try:
        data = news_fetcher.get_news()
        if not data:
            raise HTTPException(status_code=404, detail="No news found.")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/narrative/{news_id}")
async def get_narrative(news_id: int):
    try:
        text = generate_narrative(news_id)
        if not text:
            raise HTTPException(status_code=404, detail="Narrative not found.")
        return {"narrative": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
