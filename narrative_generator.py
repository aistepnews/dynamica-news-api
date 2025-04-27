import openai
import os

# تحميل المفتاح من متغير البيئة
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_narrative(news_id):
    prompt = f"Write a deep analysis for the news article with ID {news_id}."
    
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating narrative: {e}")
        return None
