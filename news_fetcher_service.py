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

from news_fetcher import NewsAutoFetcher
from narrative_generator import generate_narrative

class NewsService:
    def __init__(self, fetch_interval=1800):
        self.fetch_interval = fetch_interval
        self.news_fetcher = NewsAutoFetcher()
        self.running = False
        self.thread = None
        logger.info("تم تهيئة خدمة جلب الأخبار")

    def start(self):
        if self.running:
            return False
        self.running = True
        self.thread = threading.Thread(target=self._run_service, daemon=True)
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
                # 1) جلب الأخبار الجديدة
                self.news_fetcher.fetch_news()

                # 2) استرجاع أحدث 10 أخبار غير معالجة
                unprocessed = self.news_fetcher.get_news(limit=10, processed=False)
                for item in unprocessed:
                    news_id   = item['id']
                    title     = item.get('title', '')
                    content   = item.get('content', '')

                    # 3) توليد أنواع مختلفة من السرد
                    for narrative_type in ["summary", "official", "critical", "analysis", "human"]:
                        narrative_text = generate_narrative(
                            news_id,
                            title,
                            content,
                            narrative_type
                        )
                        # هنا يمكنك حفظ السرد في قاعدة بياناتك أو معالجته كما تشاء
                        logger.info(f"Generated {narrative_type} for news {news_id}")

                    # 4) تعليم الخبر بأنه تمّت معالجته
                    self.news_fetcher.mark_as_processed(news_id)

                # 5) الانتظار قبل الجولة التالية
                time.sleep(self.fetch_interval)

            except Exception as e:
                logger.error(f"Error in service loop: {e}", exc_info=True)
                time.sleep(60)


if __name__ == "__main__":
    service = NewsService()
    service.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        service.stop()
