import pandas as pd
import os
import time

def save_to_excel(file_names, texts, labels):
    output_dir = os.path.join("data", "excel")
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.DataFrame({
        "File_Name": file_names,
        "Extracted_Text": texts,
        "Cluster": labels
    })
    
    timestamp = int(time.time())
    file_path = os.path.join(output_dir, f"report_{timestamp}.xlsx")
    df.to_excel(file_path, index=False)
    return file_path