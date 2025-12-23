import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
import os

# مسیر تسرکت و پاپلر را همانطور که قبلا تنظیم کردیم نگه دارید
POPPLER_PATH = r"D:\Projects\Scanner\Project\poppler\Library\bin"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_for_persian(image):
    """بهبود کیفیت تصویر برای تشخیص بهتر کلمات فارسی و انگلیسی ترکیبی"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # افزایش تضاد رنگ و حذف نویز
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return gray

def extract_text(file_path):
    config = r'--oem 3 --psm 3 -c preserve_interword_spaces=1'
    
    if file_path.lower().endswith('.pdf'):
        try:
            pages = convert_from_path(file_path, poppler_path=POPPLER_PATH, dpi=300)
            full_text = ""
            for page in pages:
                # تبدیل صفحه PDF به آرایه OpenCV برای پیش‌پردازش
                open_cv_image = np.array(page)
                processed_img = preprocess_for_persian(open_cv_image)
                text = pytesseract.image_to_string(processed_img, lang="fas+eng", config=config)
                full_text += text + "\n"
            return full_text
        except Exception as e:
            return f"Error: {e}"
    else:
        image = cv2.imread(file_path)
        if image is None: return "Image not found"
        processed_img = preprocess_for_persian(image)
        return pytesseract.image_to_string(processed_img, lang="fas+eng", config=config)