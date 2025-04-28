
import requests
from bs4 import BeautifulSoup
import hashlib
import sqlite3
import time
import re
import json
from datetime import datetime
import os

class NewsAutoFetcher:
+    def __init__(self, db_path="news_cache.db"):
+        self.db_path = db_path
+        # الآن نستخدم RSS Feed مباشرةً
+        self.sources = {
+            "step_agency": {
+                "name": "وكالة ستيب الإخبارية",
+                "url": "https://stepagency-sy.net/feed/",  # رابط الـ RSS
+                "active": True
            }
        }
        self._init_db()

    def _init_db(self):
        """تهيئة قاعدة البيانات لتخزين الأخبار"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # إنشاء جدول الأخبار إذا لم يكن موجوداً
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            image_url TEXT,
            source TEXT,
            source_url TEXT,
            published_date TEXT,
            hash TEXT UNIQUE,
            created_at TEXT,
            processed BOOLEAN DEFAULT 0
        )
        ''')

        # إنشاء جدول مصادر الأخبار
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            url TEXT UNIQUE,
            active BOOLEAN DEFAULT 1
        )
        ''')

        # التحقق من وجود المصادر الافتراضية وإضافتها إذا لم تكن موجودة
        for source_key, source_data in self.sources.items():
            cursor.execute(
                "SELECT id FROM sources WHERE url = ?",
                (source_data["url"],)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO sources (name, url, active) VALUES (?, ?, ?)",
                    (source_data["name"], source_data["url"], source_data["active"])
                )

        conn.commit()
        conn.close()

    def add_source(self, name, url, active=True):
        """إضافة مصدر جديد للأخبار"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        success = False
        message = ""
        try:
            cursor.execute(
                "INSERT INTO sources (name, url, active) VALUES (?, ?, ?)",
                (name, url, active)
            )
            conn.commit()
            success = True
            message = f"تمت إضافة المصدر {name} بنجاح"
        except sqlite3.IntegrityError:
            message = f"المصدر {url} موجود بالفعل"
        finally:
            conn.close()
        return {"success": success, "message": message}

    def get_sources(self):
        """الحصول على قائمة المصادر المتاحة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, url, active FROM sources")
        sources = [
            {"id": row[0], "name": row[1], "url": row[2], "active": bool(row[3])}
            for row in cursor.fetchall()
        ]

        conn.close()
        return sources

    def toggle_source(self, source_id, active):
        """تفعيل أو تعطيل مصدر"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE sources SET active = ? WHERE id = ?",
            (active, source_id)
        )

        conn.commit()
        conn.close()

        return {"success": True, "message": "تم تحديث حالة المصدر بنجاح"}

    def _generate_hash(self, title, content):
        """توليد قيمة تجزئة فريدة للخبر لمنع التكرار"""
        hash_content = f"{title}|{content[:100]}"
        return hashlib.md5(hash_content.encode()).hexdigest()

    def _fetch_step_agency(self):
        """جلب الأخبار من وكالة ستيب الإخبارية (HTML Scraping)"""
        news_items = []
        try:
            response = requests.get(self.sources["step_agency"]["url"])
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                news_containers = soup.select('.jeg_posts article')
                for article in news_containers:
                    title_elem = article.select_one('.jeg_post_title a')
                    if not title_elem:
                        continue
                    title = title_elem.text.strip()
                    news_url = title_elem['href']
                    image_elem = article.select_one('.jeg_thumb img')
                    image_url = image_elem['src'] if image_elem and 'src' in image_elem.attrs else ""
                    news_content = self._fetch_news_content(news_url)
                    if title and news_content:
                        news_hash = self._generate_hash(title, news_content)
                        news_items.append({
                            "title": title,
                            "content": news_content,
                            "image_url": image_url,
                            "source": self.sources["step_agency"]["name"],
                            "source_url": news_url,
                            "published_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "hash": news_hash
                        })
        except Exception as e:
            print(f"خطأ في جلب الأخبار من وكالة ستيب: {str(e)}")
        return news_items

    def _fetch_rss(self, source_name, rss_url):
        """جلب الأخبار عبر RSS Feed"""
        news_items = []
        try:
            response = requests.get(rss_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')
                for item in items:
                    title = item.title.text if item.title else ""
                    link = item.link.text if item.link else ""
                    desc = item.find('description')
                    content = desc.text.strip() if desc and desc.text else ""
                    enclosure = item.find('enclosure')
                    image_url = enclosure['url'] if enclosure and enclosure.get('url') else ""
                    pub = item.find('pubDate')
                    published_date = pub.text.strip() if pub and pub.text else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    news_hash = self._generate_hash(title, content)
                    news_items.append({
                        "title": title,
                        "content": content,
                        "image_url": image_url,
                        "source": source_name,
                        "source_url": link,
                        "published_date": published_date,
                        "hash": news_hash
                    })
        except Exception as e:
            print(f"خطأ في جلب RSS من {rss_url}: {str(e)}")
        return news_items

    def _fetch_news_content(self, url):
        """جلب محتوى الخبر من الصفحة الداخلية"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                content_elem = soup.select_one('.content-inner')
                if content_elem:
                    for elem in content_elem.select('.jeg_share_top_container, .jeg_share_bottom_container, script, style'):
                        elem.decompose()
                    paragraphs = content_elem.find_all('p')
                    return '\n\n'.join(p.text.strip() for p in paragraphs if p.text.strip())
        except Exception as e:
            print(f"خطأ في جلب محتوى الخبر: {str(e)}")
        return ""

    def fetch_news(self):
        """جلب الأخبار من جميع المصادر النشطة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, url FROM sources WHERE active = 1")
        active_sources = cursor.fetchall()
        news_count = 0
        for source_id, source_name, source_url in active_sources:
            if any(x in source_url for x in ['rss', '.xml', '/feed']):
                news_items = self._fetch_rss(source_name, source_url)
            elif "stepagency-sy.net" in source_url:
                news_items = self._fetch_step_agency()
            else:
                news_items = []
            for news in news_items:
                try:
                    cursor.execute(
                        "INSERT INTO news (title, content, image_url, source, source_url, published_date, hash, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            news["title"],
                            news["content"],
                            news["image_url"],
                            news["source"],
                            news["source_url"],
                            news["published_date"],
                            news["hash"],
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                    )
                    news_count += 1
                except sqlite3.IntegrityError:
                    pass
        conn.commit()
        conn.close()
        return {"success": True, "message": f"تم جلب {news_count} خبر جديد"}

    def get_news(self, limit=10, offset=0, processed=None):
        """الحصول على الأخبار المخزنة في قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = "SELECT id, title, content, image_url, source, source_url, published_date, created_at, processed FROM news"
        params = []
        if processed is not None:
            query += " WHERE processed = ?"
            params.append(processed)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cursor.execute(query, params)
        news = [
            {"id": row[0], "title": row[1], "content": row[2], "image_url": row[3],
             "source": row[4], "source_url": row[5], "published_date": row[6],
             "created_at": row[7], "processed": bool(row[8])}
            for row in cursor.fetchall()
        ]
        conn.close()
        return news

    def mark_as_processed(self, news_id):
        """تحديد الخبر كمعالج (تم توليد الروايات له)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE news SET processed = 1 WHERE id = ?", (news_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "تم تحديث حالة الخبر بنجاح"}

if __name__ == "__main__":
    fetcher = NewsAutoFetcher()
    result = fetcher.fetch_news()
    print(json.dumps(result, ensure_ascii=False))
    news = fetcher.get_news(limit=5)
    for item in news:
        print(f"عنوان: {item['title']}")
        print(f"المصدر: {item['source']}")
        print("-" * 50)
