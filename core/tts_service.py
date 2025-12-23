import os
import time
from gtts import gTTS
from gtts.lang import tts_langs # برای بررسی لیست زبان‌های در دسترس
import pyttsx3

class TTSService:
    def __init__(self):
        self.output_dir = os.path.join("data", "audio")
        os.makedirs(self.output_dir, exist_ok=True)
        
        try:
            self.offline_engine = pyttsx3.init()
            self.offline_engine.setProperty('rate', 160)
        except:
            self.offline_engine = None

    def text_to_speech(self, text):
        timestamp = int(time.time())
        created_files = []
        errors = []
        
        # ۱. تلاش برای تولید نسخه آنلاین
        try:
            # بررسی اینکه آیا 'fa' در لیست زبان‌های گوگل هست یا نه
            # اگر اینترنت قطع باشد یا لیست لود نشود، از fa به عنوان پیش‌فرض اجباری استفاده می‌کنیم
            try:
                supported_langs = tts_langs()
                lang_to_use = 'fa' if 'fa' in supported_langs else 'en'
            except:
                lang_to_use = 'fa' # اجبار به استفاده از فارسی حتی در صورت عدم تایید

            on_path = os.path.join(self.output_dir, f"voice_{timestamp}_online.mp3")
            
            # ایجاد با پارامترهای اضافه برای جلوگیری از خطا
            tts = gTTS(text=text, lang=lang_to_use, slow=False)
            tts.save(on_path)
            
            if os.path.exists(on_path) and os.path.getsize(on_path) > 100:
                created_files.append(f"ONLINE:{on_path}")
        except Exception as e:
            errors.append(f"Online Failed: {str(e)}")

        # ۲. تولید نسخه آفلاین (همیشه)
        if self.offline_engine:
            try:
                off_path = os.path.join(self.output_dir, f"voice_{timestamp}_offline.mp3")
                self.offline_engine.save_to_file(text, off_path)
                self.offline_engine.runAndWait()
                time.sleep(0.5)
                if os.path.exists(off_path):
                    created_files.append(f"OFFLINE:{off_path}")
            except Exception as e:
                errors.append(f"Offline Failed: {str(e)}")

        if not created_files:
            return "Error: All methods failed."
        
        result = "|".join(created_files)
        if errors:
            result += f"|LOG:{errors[0]}"
        return result