import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, scrolledtext,messagebox
import threading
import whisper
import GPUtil
import numpy as np
import sounddevice as sd
import librosa
import soundfile as sf
from pydub import AudioSegment
import re
import ffmpeg
import tempfile

class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.audio_data = None
        self.fs = 16000
        self.model = None  
        self.model_loaded = False  
        self.available_vram = None
        self.video_clip = None
        self.processed_audio = None
        self.setup_ui()
        self.ensure_audio_folder()

    def ensure_audio_folder(self):
        self.audio_folder = os.path.join(os.getcwd(), "audio_files")
        if not os.path.exists(self.audio_folder):
            os.makedirs(self.audio_folder)

    def setup_ui(self):
        self.dropdown_label = ttk.Label(self, text="Model:")
        self.dropdown_label.pack(pady=(10, 5))

        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(self, textvariable=self.model_var,
                                           values=["tiny", "base", "small", "medium", "large"],
                                           state="readonly")
        self.model_dropdown.pack(pady=(0, 10))
        self.model_dropdown.bind("<<ComboboxSelected>>", self.check_requirements_and_load)

        self.progress = ttk.Progressbar(self, mode='indeterminate')
        self.status_label = ttk.Label(self, text="Chọn model để tải.")
        self.status_label.pack(pady=(10, 5))

        self.upload_button = ttk.Button(self, text="Upload Audio", command=self.upload_audio)
        self.upload_button.pack(pady=(10, 5))

        self.keyword_entry = ttk.Entry(self, width=50)
        self.keyword_entry.pack(pady=(5, 10))
        self.keyword_entry.insert(0, "Ấn keyword muốn lọc")

        self.process_button = ttk.Button(self, text="Process Audio", command=self.process_audio, state='disabled')
        self.process_button.pack(pady=(10, 5))

        self.transcription_text = scrolledtext.ScrolledText(self, width=60, height=10)
        self.transcription_text.pack(pady=(10, 5))

        self.save_button = ttk.Button(self, text="Save Output Audio", command=self.save_audio)
        self.save_button.pack(pady=(5, 10))
        self.save_button['state'] = 'disabled'
    def upload_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Media files", "*.wav *.mp3 *.ogg *.flac *.mp4")])
        if file_path:
            if file_path.endswith('.mp4'):
                self.video_clip = file_path  
                temp_audio_path = os.path.join(tempfile.gettempdir(), "temp_audio.wav")
                ffmpeg.input(file_path).output(temp_audio_path, acodec='pcm_s16le', ac=1, ar=self.fs).run(overwrite_output=True)
                audio, sr = librosa.load(temp_audio_path, sr=self.fs)
                self.audio_data = audio.astype(np.float32)
                self.status_label.config(text="Video and audio loaded successfully.")
            else:
                self.video_clip = None  
                audio, sr = librosa.load(file_path, sr=self.fs)
                self.audio_data = audio.astype(np.float32)
                self.status_label.config(text="Audio file loaded successfully.")
            self.process_button['state'] = 'normal'

    def check_requirements_and_load(self, event):
        model_choice = self.model_var.get()
        model_requirements = {"tiny": 1, "base": 1, "small": 2, "medium": 5, "large": 10}
        required_vram = model_requirements[model_choice]
        if self.check_gpu_vram(required_vram):
            self.status_label.configure(text=f"Đang tải model {model_choice}, vui lòng chờ...")
            self.progress.pack(pady=20)
            threading.Thread(target=self.load_model, args=(model_choice,), daemon=True).start()
        else:
            self.status_label.configure(text=f"Model {model_choice} yêu cầu ít nhất {required_vram} GB VRAM. Card đồ họa của bạn hiện tại chỉ có {self.available_vram} GB VRAM")
    def check_gpu_vram(self, required_vram):
        gpus = GPUtil.getGPUs()
        if not gpus:
            return False
        self.available_vram = max(gpu.memoryFree for gpu in gpus) / 1024
        return self.available_vram >= required_vram
    def load_model(self, model_name):
        self.progress.start()
        self.model = whisper.load_model(model_name)
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.configure(text=f"Đã tải xong model: {model_name}")
        self.model_loaded = True
        self.process_button['state'] = 'normal'
    def process_audio(self):
        keyword_text = self.keyword_entry.get()
        self.keywords = [k.strip().lower() for k in keyword_text.split(',') if k.strip()]
        if self.model_loaded and self.audio_data is not None:
            self.process_button['state'] = 'disabled'  # Disable the butt
            self.status_label.config(text="Processing audio...")
            threading.Thread(target=self.model_transcription, daemon=True).start()
        else:
            self.status_label.config(text="Load cả model và âm thanh đi đã.")
    def model_transcription(self):
        audio_path = os.path.join(self.audio_folder, "temp_audio.wav")
        sf.write(audio_path, self.audio_data, self.fs)
        result = self.model.transcribe(audio_path, word_timestamps=True,language="vi")
        transcription = result["text"]
        self.transcription_text.delete('1.0', tk.END)
        self.transcription_text.insert(tk.END, transcription)
        self.status_label.config(text="Đã xử lý âm thanh. Thành công")
        self.mute_keywords(result)
        self.process_button['state'] = 'normal'
        #print(result)
    @staticmethod
    def clean_text(input_text):
        cleaned_text = re.sub(r'[^\w\s]', '', input_text)  
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text) 
        return cleaned_text.strip().lower()
    def mute_keywords(self, result):
        audio_path = os.path.join(self.audio_folder, "temp_audio.wav")
        audio = AudioSegment.from_wav(audio_path)

        for segment in result['segments']:
            words = [App.clean_text(word_info['word']) for word_info in segment['words']]  
            starts = [word_info['start'] * 1000 for word_info in segment['words']] 
            ends = [word_info['end'] * 1000 for word_info in segment['words']]  

            for i, word_text in enumerate(words):
                if word_text in self.keywords:
                    start_ms = starts[i]
                    end_ms = ends[i]
                    silence = AudioSegment.silent(duration=(end_ms - start_ms))
                    audio = audio[:start_ms] + silence + audio[end_ms:]

                for j in range(i + 1, len(words) + 1):
                    phrase = " ".join(words[i:j])
                    if phrase in self.keywords:
                        start_ms = starts[i]
                        end_ms = ends[j - 1]
                        silence = AudioSegment.silent(duration=(end_ms - start_ms))
                        audio = audio[:start_ms] + silence + audio[end_ms:]
                        break  

        temp_processed_path = os.path.join(tempfile.gettempdir(), "processed_audio.wav")
        audio.export(temp_processed_path, format="wav")
        self.processed_audio = audio  
        self.temp_processed_path = temp_processed_path 
        self.save_button['state'] = 'normal'
        self.status_label.config(text="Audio processing complete with keywords muted.")
    def save_audio(self):
        if self.video_clip and self.temp_processed_path:  
            file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
            if file_path: 
                input_video = ffmpeg.input(self.video_clip)
                input_audio = ffmpeg.input(self.temp_processed_path)
                (
                    ffmpeg
                    .concat(
                        input_video.video.filter('fps', fps=24, round='up'), 
                        input_audio,
                        v=1,
                        a=1
                    )
                    .output(file_path, vcodec='libx264', acodec='aac', strict='experimental')
                    .run()
                )
                messagebox.showinfo("Save Video", "Video saved successfully with processed audio!")
        else:  
            file_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])
            if file_path: 
                if self.processed_audio:  
                    self.processed_audio.export(file_path, format="mp3")
                    messagebox.showinfo("Save Audio", "Audio saved successfully!")
                else:
                    messagebox.showerror("Error", "No processed audio available to save.")

if __name__ == "__main__":
    root = tk.Tk()
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")
    root.title("App lọc từ")
    root.geometry('800x600')
    app = App(root)
    root.mainloop()
