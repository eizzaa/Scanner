import speech_recognition as sr

class STTManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_data = None
        # تنظیمات حساسیت میکروفون
        self.recognizer.energy_threshold = 4000  # مقدار بالاتر برای محیط‌های نویزی
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0  # مکث مجاز بین کلمات (ثانیه)

    def capture_audio(self):
        try:
            with sr.Microphone() as source:
                # حذف نویز محیط قبل از شروع ضبط
                self.recognizer.adjust_for_ambient_noise(source, duration=1.2)
                # ضبط صدا - حذف محدودیت زمانی برای جملات طولانی
                audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=None)
                self.audio_data = audio
                return audio
        except Exception as e:
            print(f"Capture Error: {e}")
            return None

    def recognize(self, audio, lang_code="fa-IR"):
        if audio is None:
            return "Error: No audio captured"
        
        try:
            # ارسال به گوگل با کد زبان مشخص شده
            text = self.recognizer.recognize_google(audio, language=lang_code)
            return text
        except sr.UnknownValueError:
            return "Error: Speech was unintelligible"
        except sr.RequestError:
            return "Error: Internet connection issue"
        except Exception as e:
            return f"Error: {str(e)}"

    def stop_capture(self):
        # برای توقف دستی در برخی متدها
        pass
