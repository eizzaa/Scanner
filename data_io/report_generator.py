import os

def generate_summary(file_names, texts, labels, relationships):
    output_file = os.path.join("data/outputs", "summary_report.txt")
    os.makedirs("data/outputs", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for i, name in enumerate(file_names):
            f.write(f"مدرک {i+1} ({name}):\n")
            f.write(f"متن: {texts[i]}\n")
            f.write(f"خوشه: {labels[i]}\n\n")
        f.write("روابط شناسایی شده:\n")
        for r in relationships:
            f.write(r + "\n")
    return f"گزارش خلاصه ذخیره شد: {output_file}"
