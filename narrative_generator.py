import openai
import os

# المفتاح الآن من متغيّر البيئة OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_narrative(title: str, content: str) -> str:
    prompt = (
        f"Write a deep analysis for the following news article.\n\n"
        f"Title: {title}\n\n"
        f"Content:\n{content}\n\n"
        f"Analysis:"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
