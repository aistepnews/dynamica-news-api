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
    try:
        news_fetcher.fetch_news()
        data = news_fetcher.get_news(limit=limit, processed=processed)
        if not isinstance(data, list):
            raise HTTPException(status_code=500, detail="Invalid data format")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/narrative/{news_id}")
async def get_narrative(news_id: int):
    try:
        text = generate_narrative(news_id)
        return {"narrative": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
