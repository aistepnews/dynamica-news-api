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
+    # جيب أولاً عنوان ومحتوى الخبر من قاعدة البيانات
+    item = news_fetcher.get_news(limit=1, offset=0, processed=None)
+    item = next((n for n in item if n["id"] == news_id), None)
+    if not item:
+        raise HTTPException(status_code=404, detail="خبر غير موجود.")
+    # مّرر الـtitle والـcontent
+    text = generate_narrative(news_id, item["title"], item["content"])
     if not text:
         raise HTTPException(status_code=404, detail="Narrative not found.")
     return {"narrative": text}
