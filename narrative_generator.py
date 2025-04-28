import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("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
")

def generate_narrative(news_id: int) -> str:
    prompt = f"Write a deep analysis for the news article with ID {news_id}."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000
    )
    return response.choices[0].text.strip()
