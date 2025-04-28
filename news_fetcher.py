import requests
from bs4 import BeautifulSoup
import hashlib
import sqlite3
import os
from datetime import datetime

class NewsAutoFetcher:
    def __init__(self, db_path="news_cache.db"):
        self.db_path = db_path
        # الآن نستخدم RSS Feed مباشرةً
        self.sources = {
            "step_agency": {
                "name": "وكالة ستيب الإخبارية",
                "url": "https://stepagency-sy.net/feed/",
                "active": True
            }
        }
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

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

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                url TEXT UNIQUE,
                active BOOLEAN DEFAULT 1
            )
        ''')

        # نمسح كل المدخلات القديمة في جدول المصادر
        cursor.execute("DELETE FROM sources")

        # نعيد إدخال المصدر الوحيد برابط الـRSS الجديد
        for src in self.sources.values():
            cursor.execute(
                "INSERT INTO sources (name, url, active) VALUES (?, ?, ?)",
                (src["name"], src["url"], src["active"])
            )

        conn.commit()
        conn.close()

    def fetch_news(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, url FROM sources WHERE active = 1")
        active_sources = cursor.fetchall()
        news_count = 0

        for source_name, source_url in active_sources:
            # كل رابط فيه rss أو feed يدخل دالة الـ RSS
            if any(token in source_url for token in ('rss', 'xml', 'feed')):
                items = self._fetch_rss(source_name, source_url)
            else:
                items = []
            for news in items:
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
                    # خبر مكرر، نتجنّب الإدخال
                    pass

        conn.commit()
        conn.close()
        return {"success": True, "message": f"تم جلب {news_count} خبر جديد"}

    def _generate_hash(self, title, content):
        return hashlib.md5(f"{title}|{content[:100]}".encode()).hexdigest()

    def _fetch_rss(self, source_name, rss_url):
        news_items = []
        try:
            r = requests.get(rss_url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, "xml")
                for item in soup.find_all("item"):
                    title = item.title.text if item.title else ""
                    link = item.link.text if item.link else ""
                    desc = item.find("description")
                    content = desc.text.strip() if desc and desc.text else ""
                    enclosure = item.find("enclosure")
                    image_url = enclosure["url"] if enclosure and enclosure.get("url") else ""
                    pub = item.find("pubDate")
                    published_date = pub.text.strip() if pub and pub.text else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    h = self._generate_hash(title, content)
                    news_items.append({
                        "title": title,
                        "content": content,
                        "image_url": image_url,
                        "source": source_name,
                        "source_url": link,
                        "published_date": published_date,
                        "hash": h
                    })
        except Exception as e:
            print(f"خطأ في جلب RSS من {rss_url}: {e}")
        return news_items

    def get_news(self, limit=10, offset=0, processed=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = "SELECT id, title, content, image_url, source, source_url, published_date, processed FROM news"
        params = []
        if processed is not None:
            query += " WHERE processed = ?"
            params.append(processed)
        query += " ORDER BY published_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": r[0], "title": r[1], "content": r[2],
                "image_url": r[3], "source": r[4],
                "source_url": r[5], "published_date": r[6],
                "processed": bool(r[7])
            }
            for r in rows
        ]

    def mark_as_processed(self, news_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE news SET processed = 1 WHERE id = ?", (news_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "تم تحديث حالة الخبر بنجاح"}

    def get_news_by_id(self, news_id: int):
        """إرجاع خبر واحد حسب الـ id أو None إذا لم يوجد."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, content, image_url, source, source_url, published_date, created_at, processed
            FROM news WHERE id = ?
        """, (news_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "image_url": row[3],
            "source": row[4],
            "source_url": row[5],
            "published_date": row[6],
            "created_at": row[7],
            "processed": bool(row[8])
        }

