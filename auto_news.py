import requests

def auto_fetch_news():
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=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"
    response = requests.get(url)
    data = response.json()
    return data['articles']
