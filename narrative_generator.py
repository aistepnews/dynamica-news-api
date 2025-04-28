# narrative_generator.py

import os
import openai

# يقرأ المفتاح من متغيّر البيئة OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_narrative(title, content):
    prompt = (
        f"اكتب تحليلًا معمقًا لهذا الخبر:\n\n"
        f"العنوان: {title}\n\n"
        f"النص: {content}"
    )

    # استخدم ChatCompletion لو كانت مكتبتك >=1.0.0
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()
