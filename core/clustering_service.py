# Project/core/clustering_service.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def cluster_texts(texts):
    if len(texts) < 2:
        return ["دسته عمومی"] * len(texts)
    
    try:
        # تبدیل متن به اعداد (Vectorization)
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(texts)
        
        # تعداد خوشه‌ها (حداکثر ۳ یا به تعداد فایل‌ها)
        num_clusters = min(3, len(texts))
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        
        return [f"گروه {l + 1}" for l in labels]
    except:
        return ["خطا در خوشه‌بندی"] * len(texts)