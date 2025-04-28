@app.get("/news")
async def get_news_list():
    return [
        {"id": 1, "title": "خبر تجريبي", "content": "هذا محتوى تجريبي"},
        {"id": 2, "title": "خبر آخر",    "content": "محتوى ثاني"}
    ]
