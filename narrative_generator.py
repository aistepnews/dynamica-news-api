import os
# نلغي أي بروكسيات
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)

import openai

# افتح المفتاح مباشرة
openai.api_key = "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"

def generate_narrative(title: str, content: str) -> str:
    prompt = (
        f"Write a deep analysis for the following news article:\n\n"
        f"Title: {title}\n\n"
        f"Content:\n{content}\n\n"
        f"Please provide a detailed analytical narrative."
    )

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1000
    )
    return response.choices[0].text.strip()
