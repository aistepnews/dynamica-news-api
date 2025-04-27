import requests

def auto_fetch_news():
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=YOUR_API_KEY"
    response = requests.get(url)
    data = response.json()
    return data['articles']
