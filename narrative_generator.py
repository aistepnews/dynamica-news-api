# narrative_generator.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
# اختر نموذجًا يناسبك؛ هنا gpt2-medium كمثال
HF_API_URL = "https://api-inference.huggingface.co/models/gpt2-medium"

def generate_narrative(news_id, title, content):
    prompt = (
        f"Deep analysis of the following news article:\n"
        f"Title: {title}\n\n"
        f"Content:\n{content}\n\n"
        f"Please provide a thoughtful, in-depth analysis."
    )
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,    # قلّل إن أردت
            "temperature": 0.7
        }
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    # النتيجة غالبًا قائمة من نتائج التوليد
    generated = data[0].get("generated_text", "")
    # البادئة الحالية تحتوي على prompt + التوليد؛ نوّقع فيها:
    return generated[len(prompt):].strip()
