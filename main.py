from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Dynamica News API!"}

@app.get("/news")
async def get_news_list():
    return [
        {"id": 1, "title": "خبر تجريبي", "content": "هذا محتوى تجريبي"},
        {"id": 2, "title": "خبر آخر",    "content": "محتوى ثاني"}
    ]

@app.get("/narrative/{news_id}")
async def get_narrative(news_id: int):
    return {"narrative": f"هذه رواية تجريبية للخبر رقم {news_id}"}
