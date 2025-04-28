# src/narrative_generator.py

import os
import requests

# اقرأ التوكن من متغيّر البيئة HUGGINGFACE_API_TOKEN
HF_TOKEN = os.environ["HUGGINGFACE_API_TOKEN"]

# استدعاء نموذج مناسب (مثال: facebook/bart-large-cnn للتحليل/التلخيص العميق)
HF_MODEL = "facebook/bart-large-cnn"
API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Accept": "application/json"
}

def generate_narrative(title: str, content: str) -> str:
    """
    يُرسل العنوان والمحتوى إلى نموذج HF للحصول على تحليل معمق.
    """
    prompt = (
        f"العنوان: {title}\n\n"
        f"المحتوى:\n{content}\n\n"
        f"قدّم تحليلًا معمقًا احترافيًا لهذا الخبر."
    )
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 512,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # HF غالبًا يرجّع قائمة من المخرجات
    if isinstance(data, list) and len(data) and "generated_text" in data[0]:
        return data[0]["generated_text"].strip()
    # في حال تنسيق مختلف:
    raise ValueError("Unexpected response from HuggingFace API")
