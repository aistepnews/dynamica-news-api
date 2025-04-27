from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from news_fetcher import NewsAutoFetcher

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

# دالة مؤقتة عشان تبين لك الخطأ الكامل
@app.get("/news")
async def get_news_list():
    news_fetcher.fetch_news()                     # هنا لو فيه Exception رح يطلع
    news_data = news_fetcher.get_news(limit=10, processed=False)
    return news_data                              # لو فيه مشكلة، رح تشوف Traceback كامل

@app.get("/narrative/{news_id}")
async def get_narrative(news_id: int):
    text = generate_narrative(news_id)
    return {"narrative": text}
