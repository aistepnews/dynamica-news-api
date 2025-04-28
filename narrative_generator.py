# src/narrative_generator.py

from transformers import pipeline
from functools import lru_cache

# نحمل الموديل مرّة وحدة عند بدء التشغيل
@lru_cache(maxsize=1)
def get_summarizer():
    # يمكنك اختيار موديل أخف لو تحب: "sshleifer/distilbart-cnn-12-6"
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def generate_narrative(news_id: int, title: str, content: str) -> str:
    prompt = (
        f"عنوان الخبر: {title}\n\n"
        f"المحتوى:\n{content}\n\n"
        "اكتب تحليلًا معمقًا احترافيًا لهذا الخبر:"
    )
    summarizer = get_summarizer()
    # يقلّل الحجم لو المحتوى طويل جداً
    text_to_send = prompt if len(prompt) < 1000 else prompt[:1000] + " …"
    result = summarizer(
        text_to_send,
        max_length=300,
        min_length=100,
        do_sample=False
    )
    # pipeline بترجع list[{"summary_text": "..."}]
    return result[0]["summary_text"].strip()
