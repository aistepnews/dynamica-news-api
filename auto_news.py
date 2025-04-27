from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import os
import sys

# إضافة المسار إلى الخدمات
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.news_fetcher import NewsAutoFetcher
from app.services.narrative_generator import NarrativeGenerator

router = APIRouter()

# نماذج البيانات
class NewsSource(BaseModel):
    name: str
    url: str
    active: bool = True

class NewsItem(BaseModel):
    id: int
    title: str
    content: str
    image_url: Optional[str] = None
    source: str
    source_url: str
    published_date: str
    created_at: str
    processed: bool

class NewsNarrative(BaseModel):
    news_id: int
    narrative_type: str
    content: str

class FetchResult(BaseModel):
    success: bool
    message: str

# إنشاء كائنات الخدمات
news_fetcher = NewsAutoFetcher()
narrative_generator = NarrativeGenerator()

# وظيفة لتشغيل جلب الأخبار في الخلفية
def fetch_news_background():
    return news_fetcher.fetch_news()

# وظيفة لتوليد الروايات في الخلفية
def generate_narratives_background(news_id: int, title: str, content: str):
    # توليد جميع أنواع الروايات
    narrative_types = ["summary", "official", "critical", "analysis", "human"]
    for narrative_type in narrative_types:
        narrative_generator.generate_narrative(news_id, title, content, narrative_type)
    
    # تحديث حالة الخبر
    news_fetcher.mark_as_processed(news_id)

# واجهات برمجة التطبيقات للمصادر
@router.get("/sources", response_model=List[dict])
async def get_sources():
    """الحصول على قائمة مصادر الأخبار"""
    return news_fetcher.get_sources()

@router.post("/sources", response_model=dict)
async def add_source(source: NewsSource):
    """إضافة مصدر جديد للأخبار"""
    return news_fetcher.add_source(source.name, source.url, source.active)

@router.put("/sources/{source_id}", response_model=dict)
async def update_source(source_id: int, active: bool):
    """تحديث حالة مصدر الأخبار"""
    return news_fetcher.toggle_source(source_id, active)

# واجهات برمجة التطبيقات للأخبار
@router.get("/fetch", response_model=dict)
async def fetch_news(background_tasks: BackgroundTasks):
    """جلب الأخبار من المصادر النشطة"""
    # تشغيل المهمة في الخلفية
    background_tasks.add_task(fetch_news_background)
    return {"success": True, "message": "بدأت عملية جلب الأخبار في الخلفية"}

@router.get("/news", response_model=List[NewsItem])
async def get_news(limit: int = 10, offset: int = 0, processed: Optional[bool] = None):
    """الحصول على قائمة الأخبار"""
    return news_fetcher.get_news(limit, offset, processed)

@router.get("/news/{news_id}/narratives", response_model=dict)
async def get_news_narratives(news_id: int):
    """الحصول على جميع روايات الخبر"""
    return narrative_generator.get_all_narratives(news_id)

@router.get("/news/{news_id}/narrative/{narrative_type}", response_model=str)
async def get_news_narrative(news_id: int, narrative_type: str):
    """الحصول على رواية محددة للخبر"""
    narrative = narrative_generator.get_narrative(news_id, narrative_type)
    if narrative is None:
        # محاولة توليد الرواية إذا لم تكن موجودة
        news_items = news_fetcher.get_news(limit=1, offset=0)
        if not news_items:
            raise HTTPException(status_code=404, detail="الخبر غير موجود")
        
        news = news_items[0]
        narrative = narrative_generator.generate_narrative(
            news_id, news["title"], news["content"], narrative_type
        )
    
    return narrative

@router.post("/news/{news_id}/generate-narratives", response_model=dict)
async def generate_narratives(news_id: int, background_tasks: BackgroundTasks):
    """توليد جميع روايات الخبر"""
    # البحث عن الخبر
    news_items = news_fetcher.get_news(limit=1, offset=0)
    if not news_items:
        raise HTTPException(status_code=404, detail="الخبر غير موجود")
    
    news = news_items[0]
    
    # تشغيل المهمة في الخلفية
    background_tasks.add_task(
        generate_narratives_background,
        news_id,
        news["title"],
        news["content"]
    )
    
    return {"success": True, "message": "بدأت عملية توليد الروايات في الخلفية"}

@router.get("/status", response_model=dict)
async def get_status():
    """الحصول على حالة النظام"""
    # إحصائيات بسيطة
    news = news_fetcher.get_news(limit=1000, offset=0)
    processed_count = sum(1 for item in news if item["processed"])
    
    return {
        "total_news": len(news),
        "processed_news": processed_count,
        "sources_count": len(news_fetcher.get_sources()),
        "narrative_generator_status": "جاهز" if narrative_generator.model_loaded else "يعمل في وضع الاحتياطي"
    }
