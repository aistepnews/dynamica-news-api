# في ملف narrative_generator.py
import openai

def generate_narrative(news_id):
    openai.api_key = 'YOUR_OPENAI_API_KEY'
    
    prompt = f"Write a deep analysis for the news article with ID {news_id}."
    
    response = openai.Completion.create(
        engine="text-davinci-003",  # اختر المحرك المناسب
        prompt=prompt,
        max_tokens=1000
    )
    
    return response.choices[0].text.strip()
