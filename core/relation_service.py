# Project/core/relation_service.py
import re

def analyze_relationships(texts):
    results = []
    # الگوهای شناسایی (مثلاً کد ملی یا شماره موبایل)
    patterns = {
        "کد ملی": r'\d{10}',
        "شماره تماس": r'09\d{9}',
        "ایمیل": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    }

    for i, text in enumerate(texts):
        found_in_doc = []
        for label, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                found_in_doc.append(f"{label}: {', '.join(set(matches))}")
        
        if found_in_doc:
            results.append(f"مدرک شماره {i+1}: " + " | ".join(found_in_doc))
        else:
            results.append(f"مدرک شماره {i+1}: رابطه خاصی یافت نشد.")
            
    return results