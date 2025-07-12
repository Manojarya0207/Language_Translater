import tkinter as tk
from tkinter import ttk, messagebox
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import os
import threading
import pygame
from io import BytesIO

class LanguageTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Magic Translator")
        self.root.geometry("1000x1000")
        self.root.resizable(False, False)
        
        # Initialize translator
        self.translator = Translator()
        
        # Initialize pygame mixer for audio
        pygame.mixer.init()
        
        # Language codes for our supported languages
        self.language_codes = {
            'English': 'en',
            'Kannada': 'kn',
            'Hindi': 'hi'
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = tk.LabelFrame(main_frame, text="Input Text", padx=10, pady=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.input_text = tk.Text(input_frame, height=8, font=('Arial', 12))
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Controls section
        controls_frame = tk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Source language
        tk.Label(controls_frame, text="From:").grid(row=0, column=0, padx=5)
        self.source_lang = ttk.Combobox(controls_frame, values=list(self.language_codes.keys()), state="readonly")
        self.source_lang.current(0)  # Default to English
        self.source_lang.grid(row=0, column=1, padx=5)
        
        # Target language
        tk.Label(controls_frame, text="To:").grid(row=0, column=2, padx=5)
        self.target_lang = ttk.Combobox(controls_frame, values=list(self.language_codes.keys()), state="readonly")
        self.target_lang.current(1)  # Default to Kannada
        self.target_lang.grid(row=0, column=3, padx=5)
        
        # Buttons
        translate_btn = tk.Button(controls_frame, text="Translate", command=self.translate_text)
        translate_btn.grid(row=0, column=4, padx=5)
        
        speak_input_btn = tk.Button(controls_frame, text="Speak Input", command=self.speak_input)
        speak_input_btn.grid(row=0, column=5, padx=5)
        
        clear_btn = tk.Button(controls_frame, text="Clear", command=self.clear_text)
        clear_btn.grid(row=0, column=6, padx=5)
        
        # Output section
        output_frame = tk.LabelFrame(main_frame, text="Translated Text", padx=10, pady=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(output_frame, height=8, font=('Arial', 12), state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Output buttons
        output_btn_frame = tk.Frame(output_frame)
        output_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        speak_output_btn = tk.Button(output_btn_frame, text="Speak Translation", command=self.speak_output)
        speak_output_btn.pack(side=tk.LEFT, padx=5)
        
        copy_btn = tk.Button(output_btn_frame, text="Copy", command=self.copy_output)
        copy_btn.pack(side=tk.LEFT, padx=5)
    
    def translate_text(self):
        try:
            # Get input text
            text = self.input_text.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Warning", "Please enter text to translate")
                return
            
            # Get language codes
            src_lang = self.language_codes[self.source_lang.get()]
            dest_lang = self.language_codes[self.target_lang.get()]
            
            # Translate
            translated = self.translator.translate(text, src=src_lang, dest=dest_lang)
            
            # Display output
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, translated.text)
            self.output_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Translation failed: {str(e)}")
    
    def speak_input(self):
        self.speak_text(self.input_text.get("1.0", tk.END).strip(), self.source_lang.get())
    
    def speak_output(self):
        self.speak_text(self.output_text.get("1.0", tk.END).strip(), self.target_lang.get())
    
    def speak_text(self, text, lang_name):
        try:
            if not text:
                messagebox.showwarning("Warning", "No text to speak")
                return
            
            lang_code = self.language_codes[lang_name]
            
            # Run in a separate thread to prevent GUI freezing
            threading.Thread(target=self._speak, args=(text, lang_code), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Text-to-speech failed: {str(e)}")
    
    def _speak(self, text, lang_code):
        try:
            # Create in-memory file
            fp = BytesIO()
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.write_to_fp(fp)
            fp.seek(0)
            
            # Load and play the audio
            pygame.mixer.music.load(fp)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
    
    def clear_text(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def copy_output(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Info", "Translation copied")

if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageTranslatorApp(root)
    root.mainloop()