from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# إعدادات السماح للاتصال من موقع GitHub Pages
origins = [
    "https://aistepnews.github.io",  # رابط الواجهة الأمامية تبعك
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "أهلاً بكم في وكالة دايناميكا الإخبارية!"}
