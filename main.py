import tkinter as tk
from tkinter import ttk, messagebox
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import asyncio
import os
import tempfile
import threading

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌐 Magic Translator ✨")
        self.root.geometry("1200x650")
        self.translator = Translator()
        self.dark_mode = False
        self.history = []  

        # --- Main Container ---
        self.main_frame = tk.Frame(root, bg="#f5f5f5")
        self.main_frame.pack(fill="both", expand=True)

        # Sidebar (History Panel)
        self.sidebar = tk.Frame(self.main_frame, width=320, bg="#eeeeee")
        self.sidebar.pack(side="right", fill="y")

        tk.Label(self.sidebar, text="📜 History", font=("Segoe UI", 14, "bold"),
                 bg="#eeeeee", fg="#333").pack(pady=10)

        # Search Bar
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.search_history)
        self.search_entry = tk.Entry(self.sidebar, textvariable=self.search_var,
                                     font=("Segoe UI", 10), width=35, bd=2, relief="solid")
        self.search_entry.pack(pady=5, padx=10)

        self.history_listbox = tk.Listbox(self.sidebar, width=42, height=30,
                                          font=("Segoe UI", 10), activestyle="none")
        self.history_listbox.pack(side="left", fill="y", padx=5, pady=5)

        scrollbar = tk.Scrollbar(self.sidebar, command=self.history_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        self.history_listbox.bind("<<ListboxSelect>>", self.load_from_history)

        # --- Content Area ---
        self.container = tk.Frame(self.main_frame, bg="#f5f5f5")
        self.container.pack(side="left", fill="both", expand=True)

        self.title_label = tk.Label(
            self.container, text="🌐 Magic Translator ✨",
            font=("Segoe UI", 22, "bold"), bg="#f5f5f5", fg="#333"
        )
        self.title_label.pack(pady=15)

        tk.Label(self.container, text="Enter text:", font=("Segoe UI", 12, "bold"),
                 bg="#f5f5f5", fg="#333").pack(pady=5)
        self.input_text = tk.Text(self.container, height=6, width=70,
                                  font=("Segoe UI", 11), bd=2, relief="solid")
        self.input_text.pack(pady=5)

        # --- Language Frame ---
        self.lang_frame = tk.Frame(self.container, bg="#f5f5f5")
        self.lang_frame.pack(pady=15)

        tk.Label(self.lang_frame, text="From:", font=("Segoe UI", 10, "bold"),
                 bg="#f5f5f5").grid(row=0, column=0, padx=5)
        self.src_lang_var = tk.StringVar()
        self.src_lang_dropdown = ttk.Combobox(
            self.lang_frame, textvariable=self.src_lang_var,
            values=list(LANGUAGES.values()), width=18, state="readonly", font=("Segoe UI", 10)
        )
        self.src_lang_dropdown.set("english")
        self.src_lang_dropdown.grid(row=0, column=1, padx=5)

        tk.Label(self.lang_frame, text="To:", font=("Segoe UI", 10, "bold"),
                 bg="#f5f5f5").grid(row=0, column=2, padx=5)
        self.dest_lang_var = tk.StringVar()
        self.dest_lang_dropdown = ttk.Combobox(
            self.lang_frame, textvariable=self.dest_lang_var,
            values=list(LANGUAGES.values()), width=18, state="readonly", font=("Segoe UI", 10)
        )
        self.dest_lang_dropdown.set("hindi")
        self.dest_lang_dropdown.grid(row=0, column=3, padx=5)

        # --- Buttons ---
        self.btn_frame = tk.Frame(self.container, bg="#f5f5f5")
        self.btn_frame.pack(pady=10)

        self.make_button(self.btn_frame, "Translate", self.translate_text, "#4CAF50", 0)
        self.make_button(self.btn_frame, "Swap", self.swap_languages, "#FF9800", 1)
        self.make_button(self.btn_frame, "Dark Mode", self.toggle_dark_mode, "#9C27B0", 2)

        # --- Output Section ---
        tk.Label(self.container, text="Translated text:", font=("Segoe UI", 12, "bold"),
                 bg="#f5f5f5", fg="#333").pack(pady=5)
        self.output_text = tk.Text(self.container, height=6, width=70,
                                   font=("Segoe UI", 11), state="disabled",
                                   bd=2, relief="solid")
        self.output_text.pack(pady=5)

        # --- Extra Buttons ---
        self.extra_btn_frame = tk.Frame(self.container, bg="#f5f5f5")
        self.extra_btn_frame.pack(pady=15)

        self.make_button(self.extra_btn_frame, "📋 Copy", self.copy_output, "#2196F3", 0)
        self.make_button(self.extra_btn_frame, "🔊 Speak", self.speak_output, "#E91E63", 1)
        self.make_button(self.extra_btn_frame, "💾 Save", self.save_output, "#FFC107", 2)

    # --- Helper to create styled buttons ---
    def make_button(self, parent, text, cmd, color, col):
        btn = tk.Button(
            parent, text=text, command=cmd, bg=color, fg="white",
            font=("Segoe UI", 11, "bold"), relief="flat", padx=15, pady=6
        )
        btn.grid(row=0, column=col, padx=8)
        btn.bind("<Enter>", lambda e: btn.config(bg=self.shade(color, -20)))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))

    def shade(self, hex_color, percent):
        hex_color = hex_color.lstrip("#")
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        shaded = tuple(max(0, min(255, int(c + (percent/100)*255))) for c in rgb)
        return "#%02x%02x%02x" % shaded

    # --- Translate Function ---
    def translate_text(self):
        try:
            text = self.input_text.get("1.0", tk.END).strip()
            src_lang = self.src_lang_var.get().lower()
            dest_lang = self.dest_lang_var.get().lower()

            if not text:
                messagebox.showwarning("⚠️ Input Error", "Please enter text to translate.")
                return

            src_code = [k for k, v in LANGUAGES.items() if v == src_lang]
            dest_code = [k for k, v in LANGUAGES.items() if v == dest_lang]

            result = self.translator.translate(text, src=src_code[0], dest=dest_code[0])
            if hasattr(result, "__await__"):
                result = asyncio.get_event_loop().run_until_complete(result)

            translated_text = result.text

            self.output_text.config(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, translated_text)
            self.output_text.config(state="disabled")

            # Save to History
            entry = f"{text[:20]}... → {translated_text[:20]}..."
            self.history.append((text, translated_text))
            self.update_history_list()

        except Exception as e:
            messagebox.showerror("❌ Error", f"Translation failed: {e}")

    # --- Update History List ---
    def update_history_list(self, filter_text=""):
        self.history_listbox.delete(0, tk.END)
        for original, translated in self.history:
            entry = f"{original[:20]}... → {translated[:20]}..."
            if filter_text.lower() in entry.lower():
                self.history_listbox.insert(tk.END, entry)

    # --- Search in History ---
    def search_history(self, *args):
        search_text = self.search_var.get()
        self.update_history_list(filter_text=search_text)

    # --- Load from History ---
    def load_from_history(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            idx = selection[0]
            filtered_items = [h for h in self.history if self.search_var.get().lower() in f"{h[0]}... → {h[1]}...".lower()]
            if idx < len(filtered_items):
                original, translated = filtered_items[idx]
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, original)
                self.output_text.config(state="normal")
                self.output_text.delete("1.0", tk.END)
                self.output_text.insert(tk.END, translated)
                self.output_text.config(state="disabled")

    # --- Swap Languages ---
    def swap_languages(self):
        src, dest = self.src_lang_var.get(), self.dest_lang_var.get()
        self.src_lang_var.set(dest)
        self.dest_lang_var.set(src)

    # --- Copy to Clipboard ---
    def copy_output(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("✅ Copied", "Translation copied to clipboard!")

    # --- Speak Output ---
    def speak_output(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if text:
            dest_lang = self.dest_lang_var.get().lower()
            lang_code = [k for k, v in LANGUAGES.items() if v == dest_lang][0]

            def play_audio():
                try:
                    tts = gTTS(text=text, lang=lang_code)
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    tts.save(temp_file.name)
                    os.system(f"start {temp_file.name}")
                except Exception as e:
                    messagebox.showerror("Error", f"Speech failed: {e}")

            threading.Thread(target=play_audio, daemon=True).start()

    # --- Save Translation to File ---
    def save_output(self):
        text = self.output_text.get("1.0", tk.END).strip()
        if text:
            with open("translations.txt", "a", encoding="utf-8") as f:
                f.write(f"\n{self.input_text.get('1.0', tk.END).strip()} --> {text}\n")
            messagebox.showinfo("💾 Saved", "Translation saved to translations.txt")

    # --- Toggle Dark Mode ---
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg = "#222" if self.dark_mode else "#f5f5f5"
        fg = "#fff" if self.dark_mode else "#333"
        sidebar_bg = "#333" if self.dark_mode else "#eeeeee"

        self.main_frame.config(bg=bg)
        self.container.config(bg=bg)
        self.title_label.config(bg=bg, fg=fg)
        self.lang_frame.config(bg=bg)
        self.btn_frame.config(bg=bg)
        self.extra_btn_frame.config(bg=bg)
        self.sidebar.config(bg=sidebar_bg)
        self.history_listbox.config(bg=sidebar_bg, fg=fg)
        self.search_entry.config(bg="#555" if self.dark_mode else "#fff", fg=fg)

        for widget in self.container.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=bg, fg=fg)

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()

