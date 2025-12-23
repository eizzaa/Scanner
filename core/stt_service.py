import speech_recognition as sr
import os

class STTManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.audio_data = None

    def capture_audio(self):
        """این متد برای ضبط است و باید در یک ترد جدا اجرا شود"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # ضبط تا زمانی که کاربر متوقف کند (در GUI مدیریت می‌شود)
            self.audio_data = self.recognizer.listen(source)
            return self.audio_data

    def recognize(self, audio):
        try:
            return self.recognizer.recognize_google(audio, language="fa-IR")
        except:
            return "Error: Could not understand audio."