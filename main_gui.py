import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import time
import threading
from core import ocr_service, tts_service, clustering_service, stt_service
from data_io import excel_exporter

# --- Smart File Confirmation Window ---
class FileConfirmWindow(ctk.CTkToplevel):
    def __init__(self, parent, file_path, action_name, on_confirm):
        super().__init__(parent)
        self.title("Confirm Action")
        self.geometry("450x400")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / 1024  # KB
        file_ext = os.path.splitext(file_name)[1].upper()
        
        ctk.CTkLabel(self, text="📋 File Information", font=("Arial", 18, "bold")).pack(pady=20)
        
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(pady=10, padx=30, fill="both", expand=True)
        
        details = (
            f"📂 Name: {file_name}\n\n"
            f"🔍 Format: {file_ext}\n\n"
            f"⚖️ Size: {file_size:.2f} KB\n\n"
            f"⚙️ Action: {action_name}"
        )
        ctk.CTkLabel(info_frame, text=details, justify="left", font=("Arial", 13)).pack(pady=20, padx=20)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        self.btn_yes = ctk.CTkButton(btn_frame, text="Confirm & Start", fg_color="#27ae60", width=120, 
                                     command=lambda: [on_confirm(), self.destroy()])
        self.btn_yes.pack(side="left", padx=10)
        
        self.btn_no = ctk.CTkButton(btn_frame, text="Cancel", fg_color="#c0392b", width=120, 
                                    command=self.destroy)
        self.btn_no.pack(side="left", padx=10)

class SmartScannerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Multi-Processor PRO")
        self.geometry("1150x850")
        ctk.set_appearance_mode("dark")
        
        # Services & State
        self.stt_manager = stt_service.STTManager()
        self.is_recording = False
        self.temp_audio_data = None
        self.last_recognized_text = ""
        self.data_store = {"texts": [], "filenames": []}
        
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar (English Layout) ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="CONTROL PANEL", font=("Arial", 22, "bold")).pack(pady=20)

        # --- Documents Section ---
        ctk.CTkLabel(self.sidebar, text="--- DOCUMENTS ---", text_color="#3498db").pack(pady=(10,5))
        ctk.CTkButton(self.sidebar, text="PDF to Photo", command=self.ui_pdf_to_photo).pack(pady=5, padx=20, fill="x")
        self.format_menu = ctk.CTkOptionMenu(self.sidebar, values=["PNG", "JPG"])
        self.format_menu.pack(pady=2, padx=40, fill="x")
        ctk.CTkButton(self.sidebar, text="PDF to Text", command=self.ui_pdf_to_text).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Photo to Text", command=self.ui_photo_to_text).pack(pady=5, padx=20, fill="x")

        # --- Smart Microphone (STT - 5 Buttons) ---
        ctk.CTkLabel(self.sidebar, text="--- MICROPHONE ---", text_color="#e74c3c").pack(pady=(20,5))
        self.timer_label = ctk.CTkLabel(self.sidebar, text="00:00", font=("Consolas", 28, "bold"), text_color="#e74c3c")
        self.timer_label.pack()

        self.btn_start = ctk.CTkButton(self.sidebar, text="1. Start Mic", fg_color="#27ae60", command=self.start_mic)
        self.btn_start.pack(pady=2, padx=20, fill="x")

        self.btn_stop = ctk.CTkButton(self.sidebar, text="2. Stop Mic", state="disabled", fg_color="#c0392b", command=self.stop_mic)
        self.btn_stop.pack(pady=2, padx=20, fill="x")

        self.btn_process = ctk.CTkButton(self.sidebar, text="3. Process Speech", state="disabled", command=self.process_speech)
        self.btn_process.pack(pady=2, padx=20, fill="x")

        self.btn_save_voice = ctk.CTkButton(self.sidebar, text="4. Save to List", state="disabled", fg_color="#2980b9", command=self.save_voice_final)
        self.btn_save_voice.pack(pady=2, padx=20, fill="x")

        self.btn_cancel = ctk.CTkButton(self.sidebar, text="5. Cancel/Reset", state="disabled", fg_color="#7f8c8d", command=self.cancel_stt)
        self.btn_cancel.pack(pady=2, padx=20, fill="x")

        # --- Text to Speech (TTS) ---
        ctk.CTkLabel(self.sidebar, text="--- TEXT TO SPEECH ---", text_color="#f1c40f").pack(pady=(20,5))
        self.tts_input = ctk.CTkEntry(self.sidebar, placeholder_text="Type text here...")
        self.tts_input.pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Convert Typed", command=self.ui_tts_typed).pack(pady=2, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Browse File for Voice", command=self.ui_tts_browse).pack(pady=2, padx=20, fill="x")

        # --- Language Selection for STT ---
        ctk.CTkLabel(self.sidebar, text="STT Language:", text_color="white").pack(pady=(10,0))
        self.stt_lang_menu = ctk.CTkOptionMenu(self.sidebar, values=["Persian", "English"])
        self.stt_lang_menu.pack(pady=5, padx=20, fill="x")
        self.stt_lang_menu.set("Persian") # مقدار پیش‌فرض

        # --- Export ---
        ctk.CTkButton(self.sidebar, text="EXPORT TO EXCEL", fg_color="#1abc9c", font=("Arial", 14, "bold"), 
                     command=self.ui_export).pack(side="bottom", pady=25, padx=20, fill="x")

        # --- Logging Console ---
        self.log_area = ctk.CTkTextbox(self, font=("Consolas", 14), corner_radius=10)
        self.log_area.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    # --- Async Runner ---
    def run_async(self, func, *args):
        threading.Thread(target=func, args=args, daemon=True).start()

    # --- STT Logic (Exactly as requested) ---
    def start_mic(self):
        self.is_recording = True
        self.start_time = time.time()
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.log("🎙️ Mic ON... Speak now.")
        threading.Thread(target=self.update_timer, daemon=True).start()
        threading.Thread(target=self.capture_thread, daemon=True).start()

    def capture_thread(self):
        self.temp_audio_data = self.stt_manager.capture_audio()

    def update_timer(self):
        while self.is_recording:
            elapsed = int(time.time() - self.start_time)
            mins, secs = divmod(elapsed, 60)
            self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
            time.sleep(1)

    def stop_mic(self):
        self.is_recording = False
        self.btn_stop.configure(state="disabled")
        self.btn_process.configure(state="normal")
        self.btn_cancel.configure(state="normal")
        self.log("🛑 Mic OFF. Click 'Process' to convert.")

    def process_speech(self):
        # دریافت زبان انتخابی از منوی جدید
        selected_lang = self.stt_lang_menu.get()
        lang_code = "fa-IR" if selected_lang == "Persian" else "en-US"
        
        self.log(f"⚙️ Processing {selected_lang} speech...")
        
        def run():
            # استفاده از temp_audio_data که در capture_thread پر شده است
            text = self.stt_manager.recognize(self.temp_audio_data, lang_code=lang_code)
            self.last_recognized_text = text
            
            # نمایش نتیجه یا خطا در لاگ
            if "Error" in text:
                self.log(f"❌ {text}")
            else:
                self.log(f"📝 Result ({selected_lang}): {text}")
                self.btn_save_voice.configure(state="normal")
            
            self.btn_process.configure(state="disabled")

        threading.Thread(target=run, daemon=True).start()

    def cancel_stt(self):
        self.is_recording = False
        self.temp_audio_data = None
        self.last_recognized_text = ""
        self.timer_label.configure(text="00:00")
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.btn_process.configure(state="disabled")
        self.btn_save_voice.configure(state="disabled")
        self.btn_cancel.configure(state="disabled")
        self.log("❌ STT Cancelled/Reset.")

    def save_voice_final(self):
        if self.last_recognized_text:
            self.data_store["texts"].append(self.last_recognized_text)
            self.data_store["filenames"].append(f"Voice_Note_{int(time.time())}")
            self.log("✅ Voice text added to Excel list.")
            self.cancel_stt()

    # --- UI Calls with Confirmation ---
    def ui_pdf_to_photo(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            FileConfirmWindow(self, path, "Convert PDF to Photo", lambda: self.run_async(self.proc_pdf_to_photo, path))

    def ui_pdf_to_text(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            FileConfirmWindow(self, path, "Extract Text from PDF", lambda: self.run_async(self.proc_pdf_to_text, path))

    def ui_photo_to_text(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if path:
            FileConfirmWindow(self, path, "Image OCR", lambda: self.run_async(self.proc_photo_to_text, path))

    def ui_tts_browse(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            FileConfirmWindow(self, path, "Convert File to Speech", lambda: self.run_async(self.proc_tts_file, path))

    # --- Background Processors ---
    def proc_pdf_to_photo(self, path):
        fmt = self.format_menu.get()
        folder = os.path.join("data", "photos", f"PDF_{int(time.time())}")
        self.log(f"⏳ Converting PDF to {fmt}...")
        images = ocr_service.pdf_to_images(path, folder, fmt=fmt)
        self.log(f"✅ Success! {len(images)} images saved.\n📍 {folder}")

    def proc_pdf_to_text(self, path):
        self.log("⏳ Extracting text from PDF...")
        text = ocr_service.extract_text(path)
        self.save_txt_file(text, os.path.basename(path))
        self.data_store["texts"].append(text)
        self.data_store["filenames"].append(os.path.basename(path))
        self.log("✅ Text extraction completed.")

    def proc_photo_to_text(self, path):
        self.log("⏳ Performing OCR on image...")
        text = ocr_service.extract_text(path)
        self.save_txt_file(text, os.path.basename(path))
        self.data_store["texts"].append(text)
        self.data_store["filenames"].append(os.path.basename(path))
        self.log("✅ OCR Done.")

    def proc_tts_file(self, path):
        self.log("⏳ Generating voice from file...")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            result = tts_service.TTSService().text_to_speech(text)
            self.handle_tts_result(result)
        except Exception as e:
            self.log(f"❌ Error: {e}")

    # --- Helpers ---
    def handle_tts_result(self, result):
        if "Error" in result: self.log(f"❌ {result}")
        else:
            for p in result.split("|"):
                if p.startswith("LOG:"): self.log(f"⚠️ {p[4:]}")
                else:
                    mode, path = p.split(":", 1)
                    self.log(f"🔊 {mode} voice saved: {path}")

    def save_txt_file(self, text, name):
        out = os.path.join("data", "texts")
        os.makedirs(out, exist_ok=True)
        p = os.path.join(out, f"{os.path.splitext(name)[0]}.txt")
        with open(p, "w", encoding="utf-8-sig") as f: f.write(text)
        return p

    def log(self, msg):
        self.log_area.insert("end", f"> {msg}\n" + "-"*40 + "\n")
        self.log_area.see("end")

    def ui_tts_typed(self):
        t = self.tts_input.get().strip()
        if t: self.run_async(lambda: self.handle_tts_result(tts_service.TTSService().text_to_speech(t)))

    def ui_export(self):
        if not self.data_store["texts"]: return
        self.log("📊 Clustering and exporting to Excel...")
        try:
            l = clustering_service.cluster_texts(self.data_store["texts"])
            p = excel_exporter.save_to_excel(self.data_store["filenames"], self.data_store["texts"], l)
            self.log(f"✅ Excel saved: {p}")
            os.startfile(os.path.dirname(p))
        except Exception as e: self.log(f"❌ Excel Error: {e}")

if __name__ == "__main__":
    app = SmartScannerApp()
    app.mainloop()
