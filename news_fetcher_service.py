import os
import sys
import time
import threading
import logging
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("news_fetcher_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("news_fetcher_service")

# إضافة المسار إلى الخدمات
sys.path.append(os.path.join(os.path.dirname(__file__), "path_to_modules"))

try:
    from app.services.news_fetcher import NewsAutoFetcher
    from app.services.narrative_generator import NarrativeGenerator
except ImportError as e:
    logger.error(f"خطأ في استيراد الوحدات: {str(e)}")
    sys.exit(1)

class NewsService:
    def __init__(self, fetch_interval=1800):  # 1800 ثانية = 30 دقيقة
        self.fetch_interval = fetch_interval
        self.news_fetcher = NewsAutoFetcher()
        self.narrative_generator = NarrativeGenerator()
        self.running = False
        self.thread = None
        logger.info("تم تهيئة خدمة جلب الأخبار")
    
    def start(self):
        """بدء خدمة جلب الأخبار"""
        if self.running:
            logger.warning("خدمة جلب الأخبار قيد التشغيل بالفعل")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._run_service)
        self.thread.daemon = True
        self.thread.start()
        logger.info("تم بدء خدمة جلب الأخبار")
        return True
    
    def stop(self):
        """إيقاف خدمة جلب الأخبار"""
        if not self.running:
            logger.warning("خدمة جلب الأخبار متوقفة بالفعل")
            return False
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("تم إيقاف خدمة جلب الأخبار")
        return True
    
    def _run_service(self):
        """تشغيل حلقة الخدمة"""
        logger.info("بدء حلقة خدمة جلب الأخبار")
        
        while self.running:
            try:
                # جلب الأخبار
                logger.info("جاري جلب الأخبار...")
                result = self.news_fetcher.fetch_news()
                logger.info(f"نتيجة جلب الأخبار: {result['message']}")
                
                # معالجة الأخبار غير المعالجة
                unprocessed_news = self.news_fetcher.get_news(limit=10, processed=False)
                logger.info(f"عدد الأخبار غير المعالجة: {len(unprocessed_news)}")
                
                for news in unprocessed_news:
                    try:
                        logger.info(f"جاري معالجة الخبر: {news['id']} - {news['title']}")
                        
                        # توليد الروايات المختلفة
                        narrative_types = ["summary", "official", "critical", "analysis", "human"]
                        for narrative_type in narrative_types:
                            self.narrative_generator.generate_narrative(
                                news['id'], news['title'], news['content'], narrative_type
                            )
                        
                        # تحديث حالة الخبر
                        self.news_fetcher.mark_as_processed(news['id'])
                        logger.info(f"تم معالجة الخبر: {news['id']}")
                    except Exception as e:
                        logger.error(f"خطأ في معالجة الخبر {news['id']}: {str(e)}")
                
                # انتظار الفترة المحددة
                logger.info(f"انتظار {self.fetch_interval} ثانية حتى الجلب التالي...")
                
                # استخدام حلقة انتظار قصيرة للسماح بالإيقاف السريع
                for _ in range(self.fetch_interval // 10):
                    if not self.running:
                        break
                    time.sleep(10)
            except Exception as e:
                logger.error(f"خطأ في حلقة الخدمة: {str(e)}")
                # انتظار قبل المحاولة مرة أخرى
                time.sleep(60)
        
        logger.info("انتهت حلقة خدمة جلب الأخبار")

# تشغيل الخدمة كبرنامج مستقل
if __name__ == "__main__":
    logger.info("بدء تشغيل خدمة جلب الأخبار كبرنامج مستقل")
    
    # إنشاء وتشغيل الخدمة
    service = NewsService()
    service.start()
    
    try:
        # الانتظار حتى يتم إيقاف البرنامج
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("تم استلام إشارة إيقاف")
        service.stop()
    
    logger.info("انتهى تشغيل خدمة جلب الأخبار")
