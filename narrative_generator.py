import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import json
import sqlite3
from datetime import datetime

class NarrativeGenerator:
    def __init__(self, model_path="local_ai_model", db_path="narratives_cache.db"):
        self.db_path = db_path
        self._init_db()
        
        # تحميل نموذج الذكاء الاصطناعي المحلي
        try:
            # محاولة تحميل نموذج محلي إذا كان متاحاً
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
            self.model_loaded = True
        except Exception as e:
            print(f"تعذر تحميل النموذج المحلي: {str(e)}")
            # استخدام نموذج بسيط في حالة عدم توفر النموذج المحلي
            self.model_loaded = False
        
        # تحميل مكتبات معالجة اللغة الطبيعية
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.arabic_stopwords = set(stopwords.words('arabic'))
        except Exception as e:
            print(f"تعذر تحميل مكتبات معالجة اللغة: {str(e)}")
            self.arabic_stopwords = set()
    
    def _init_db(self):
        """تهيئة قاعدة البيانات لتخزين الروايات المولدة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # إنشاء جدول الروايات إذا لم يكن موجوداً
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS narratives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_id INTEGER,
            narrative_type TEXT,
            content TEXT,
            created_at TEXT,
            UNIQUE(news_id, narrative_type)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _extract_keywords(self, text, top_n=10):
        """استخراج الكلمات المفتاحية من النص"""
        if not text:
            return []
        
        # تنظيف النص
        text = re.sub(r'[^\w\s]', '', text)
        
        # تقسيم النص إلى كلمات
        words = word_tokenize(text)
        
        # إزالة كلمات التوقف والكلمات القصيرة
        words = [word for word in words if word not in self.arabic_stopwords and len(word) > 2]
        
        # حساب تكرار الكلمات
        word_freq = {}
        for word in words:
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1
        
        # ترتيب الكلمات حسب التكرار
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # إرجاع أهم الكلمات
        return [word for word, freq in sorted_words[:top_n]]
    
    def _summarize_text(self, text, max_sentences=3):
        """تلخيص النص إلى عدد محدد من الجمل"""
        if not text:
            return ""
        
        # تقسيم النص إلى جمل
        sentences = sent_tokenize(text)
        
        # إذا كان عدد الجمل أقل من الحد الأقصى، إرجاع النص كاملاً
        if len(sentences) <= max_sentences:
            return text
        
        # اختيار الجمل الأولى والأخيرة
        selected_sentences = sentences[:max_sentences-1] + [sentences[-1]]
        
        # إعادة تجميع الجمل
        return ' '.join(selected_sentences)
    
    def _generate_with_ai(self, prompt, max_length=500):
        """توليد نص باستخدام نموذج الذكاء الاصطناعي"""
        if not self.model_loaded:
            return self._fallback_generation(prompt)
        
        try:
            # تحويل النص إلى توكنز
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # توليد النص
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=max_length,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )
            
            # تحويل التوكنز إلى نص
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # إزالة النص الأصلي من النص المولد
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
        except Exception as e:
            print(f"خطأ في توليد النص: {str(e)}")
            return self._fallback_generation(prompt)
    
    def _fallback_generation(self, prompt):
        """توليد نص بسيط في حالة فشل نموذج الذكاء الاصطناعي"""
        # استخراج الكلمات المفتاحية
        keywords = self._extract_keywords(prompt)
        
        # تلخيص النص
        summary = self._summarize_text(prompt)
        
        # إنشاء نص بسيط باستخدام الكلمات المفتاحية والتلخيص
        if "ملخص" in prompt.lower():
            return summary
        elif "رسمية" in prompt.lower():
            return f"وفقاً للمصادر الرسمية، {summary}"
        elif "نقدية" in prompt.lower():
            return f"من وجهة نظر نقدية، يمكن القول إن {summary}"
        elif "تحليل" in prompt.lower():
            return f"في تحليل معمق للموضوع، نجد أن {summary} ومن الجدير بالذكر أن الكلمات المفتاحية في هذا السياق هي: {', '.join(keywords[:5])}"
        elif "إنسانية" in prompt.lower():
            return f"من الناحية الإنسانية، {summary} وهذا يؤثر بشكل مباشر على حياة الناس اليومية."
        else:
            return summary
    
    def generate_narrative(self, news_id, title, content, narrative_type):
        """توليد رواية محددة للخبر"""
        # التحقق من وجود الرواية في قاعدة البيانات
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT content FROM narratives WHERE news_id = ? AND narrative_type = ?",
            (news_id, narrative_type)
        )
        existing_narrative = cursor.fetchone()
        
        if existing_narrative:
            conn.close()
            return existing_narrative[0]
        
        # إنشاء نص المطالبة حسب نوع الرواية
        if narrative_type == "summary":
            prompt = f"قم بتلخيص الخبر التالي في فقرة واحدة قصيرة: {title}. {content}"
        elif narrative_type == "official":
            prompt = f"اكتب الرواية الرسمية للخبر التالي كما وردت من المصادر الرسمية: {title}. {content}"
        elif narrative_type == "critical":
            prompt = f"قدم تحليلاً نقدياً للخبر التالي مع عرض وجهات النظر المختلفة: {title}. {content}"
        elif narrative_type == "analysis":
            prompt = f"قدم تحليلاً معمقاً للخبر التالي مع دراسة خلفياته وتداعياته المحتملة: {title}. {content}"
        elif narrative_type == "human":
            prompt = f"اكتب القصة الإنسانية للخبر التالي مع التركيز على تأثيره على حياة الناس: {title}. {content}"
        else:
            prompt = f"{title}. {content}"
        
        # توليد النص
        generated_text = self._generate_with_ai(prompt)
        
        # حفظ النص المولد في قاعدة البيانات
        cursor.execute(
            "INSERT INTO narratives (news_id, narrative_type, content, created_at) VALUES (?, ?, ?, ?)",
            (
                news_id,
                narrative_type,
                generated_text,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        
        conn.commit()
        conn.close()
        
        return generated_text
    
    def get_narrative(self, news_id, narrative_type):
        """الحصول على رواية محددة للخبر"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT content FROM narratives WHERE news_id = ? AND narrative_type = ?",
            (news_id, narrative_type)
        )
        narrative = cursor.fetchone()
        
        conn.close()
        
        if narrative:
            return narrative[0]
        else:
            return None
    
    def get_all_narratives(self, news_id):
        """الحصول على جميع الروايات المتاحة للخبر"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT narrative_type, content FROM narratives WHERE news_id = ?",
            (news_id,)
        )
        narratives = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return narratives

# نموذج لاستخدام الفئة
if __name__ == "__main__":
    generator = NarrativeGenerator()
    
    # مثال على توليد روايات مختلفة لخبر
    news_id = 1
    title = "توقيع اتفاقية تعاون اقتصادي بين دول المنطقة"
    content = """
    تم اليوم توقيع اتفاقية تعاون اقتصادي بين دول المنطقة تهدف إلى تعزيز التبادل التجاري وتنمية الاقتصاد المشترك.
    وقال وزير الاقتصاد إن هذه الاتفاقية ستسهم في زيادة حجم التبادل التجاري بنسبة 30% خلال السنوات الثلاث القادمة.
    وتتضمن الاتفاقية بنوداً تتعلق بتخفيض الرسوم الجمركية وتسهيل حركة البضائع والاستثمارات بين الدول الموقعة.
    """
    
    # توليد الروايات المختلفة
    summary = generator.generate_narrative(news_id, title, content, "summary")
    official = generator.generate_narrative(news_id, title, content, "official")
    critical = generator.generate_narrative(news_id, title, content, "critical")
    
    print("الملخص السريع:")
    print(summary)
    print("\nالرواية الرسمية:")
    print(official)
    print("\nالرواية النقدية:")
    print(critical)
