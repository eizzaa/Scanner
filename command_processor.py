# Project/command_processor.py

class CommandProcessor:
    def __init__(self, app_instance):
        """
        app_instance: نمونه‌ای از کلاس GUI برای دسترسی به متدهای آن
        """
        self.app = app_instance

    def process_and_execute(self, text: str):
        text = text.lower().strip()
        
        # تشخیص قصد کاربر (Intent Recognition)
        if any(word in text for word in ["اسکن", "scan", "بخوان", "ocr"]):
            self.app.ui_scan()
            return "در حال باز کردن انتخابگر فایل برای اسکن..."

        elif any(word in text for word in ["صدا", "voice", "بشنو", "stt", "تایپ"]):
            self.app.ui_stt()
            return "سرویس تبدیل گفتار به متن فعال شد."

        elif any(word in text for word in ["بخوان", "speak", "tts", "پخش"]):
            self.app.ui_tts()
            return "در حال آماده‌سازی برای تبدیل متن به گفتار..."

        elif any(word in text for word in ["اکسل", "excel", "خروجی", "ذخیره"]):
            self.app.ui_export()
            return "فرآیند خروجی اکسل آغاز شد."

        else:
            return "متوجه دستور نشدم. لطفا از کلماتی مثل اسکن، اکسل یا صدا استفاده کنید."