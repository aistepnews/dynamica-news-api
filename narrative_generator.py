# src/narrative_generator.py

import os
import requests

HF_TOKEN = os.environ["HUGGINGFACE_API_TOKEN"]

# نموذج مجاني مدعوم للـInference
HF_MODEL = "sshleifer/distilbart-cnn-12-6"
API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Accept": "application/json"
}

def generate_narrative(title: str, content: str) -> str:
    prompt = (
        f"عنوان الخبر: {title}\n\n"
        f"المحتوى:\n{content}\n\n"
        f"اكتب تحليلًا معمقًا احترافيًا لهذا الخبر."
    )
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 512,
            "temperature": 0.7
        }
    }

    resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list) and data and "summary_text" in data[0]:
        return data[0]["summary_text"].strip()
    if isinstance(data, dict) and "error" in data:
        raise ValueError(f"HuggingFace error: {data['error']}")
    raise ValueError("Unexpected response format from HF API")
