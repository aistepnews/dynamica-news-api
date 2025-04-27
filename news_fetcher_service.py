import os
import sys
import time
import threading
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("news_fetcher_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("news_fetcher_service")

# تصحيح الاستيرادات
from news_fetcher import NewsAutoFetcher
from narrative_generator import generate_narrative

class NewsService:
    def __init__(self, fetch_interval=1800):
        self.fetch_interval = fetch_interval
        self.news_fetcher = NewsAutoFetcher()
        self.narrative_generator = NarrativeGenerator()
        self.running = False
        self.thread = None
        logger.info("تم تهيئة خدمة جلب الأخبار")

    def start(self):
        if self.running:
            return False
        self.running = True
        self.thread = threading.Thread(target=self._run_service)
        self.thread.daemon = True
        self.thread.start()
        logger.info("تم بدء خدمة جلب الأخبار")
        return True

    def stop(self):
        if not self.running:
            return False
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("تم إيقاف خدمة جلب الأخبار")
        return True

    def _run_service(self):
        while self.running:
            try:
                result = self.news_fetcher.fetch_news()
                unprocessed_news = self.news_fetcher.get_news(limit=10, processed=False)
                for news in unprocessed_news:
                    for narrative_type in ["summary", "official", "critical", "analysis", "human"]:
                        self.narrative_generator.generate_narrative(
                            news['id'], news['title'], news['content'], narrative_type
                        )
                    self.news_fetcher.mark_as_processed(news['id'])
                time.sleep(self.fetch_interval)
            except Exception as e:
                logger.error(f"Error in service loop: {str(e)}")
                time.sleep(60)

if __name__ == "__main__":
    service = NewsService()
    service.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
