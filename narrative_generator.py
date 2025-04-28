import os
# ↙️ نلغي أي قيمة بروكسي لو موجودة:
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_narrative(title: str, content: str) -> str:
    prompt = (
        f"أعطني تحليلًا عميقًا للمقال التالي:\n\n"
        f"العنوان: {title}\n\n"
        f"المحتوى:\n{content}\n\n"
        f"الرجاء كتابة تحليل مفصل."
    )
    response = openai.completions.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=1000
    )
    return response.choices[0].text.strip()
