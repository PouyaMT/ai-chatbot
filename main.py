from pathlib import Path
import base64
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog
from ttkthemes import ThemedTk
import keyboard
import google.generativeai as genai
from openai import OpenAI

global response

# Function to encode image to base64 format
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to interact with Gemini API
def gemini(gemini_key, model, prompt, image):
    global response
    genai.configure(api_key=gemini_key)
    genai_model = genai.GenerativeModel(model_name=model)

    if model in ["gemini-pro"]:
        response = genai_model.generate_content(prompt)
    elif model in ["gemini-pro-vision"]:
        image_parts = [{"mime_type": "image/png", "data": Path(image).read_bytes()}]
        prompt_parts = [prompt, image_parts[0]]
        response = genai_model.generate_content(prompt_parts)

# Function to interact with OpenAI API
def openai(openai_key, model, prompt, image):
    global response
    client = OpenAI(api_key=openai_key)

    if model in ["gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview",
                 "gpt-3.5-turbo-1106", "gpt-3.5-turbo-16k", "gpt-3.5-turbo"]:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": f"{prompt}"}])

    elif model in ["gpt-4-vision-preview"]:
        base64_image = encode_image(image)

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{"role": "user",
                       "content": [
                           {"type": "text", "text": f"{prompt}"},
                           {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                       ]}])

    for choice in response.choices:
        response = choice.message.content

# Class to create the chatbot interface
class Chatbot:
    def __init__(self, master):
        self.master = master
        self.master.title("AI Chatbot")
        self.master.resizable(False, False)

        # Main frame
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.grid(row=0, column=0)
        self.api_keys_frame = ttk.Frame(self.master)

        # Right click menu for copy-paste operations
        self.right_click = tk.Menu(root, tearoff=0)
        self.right_click.add_command(label="Cut", command=lambda: keyboard.send('ctrl+x'), accelerator='Ctrl+X')
        self.right_click.add_command(label="Copy", command=lambda: keyboard.send('ctrl+c'), accelerator='Ctrl+C')
        self.right_click.add_command(label="Paste", command=lambda: keyboard.send('ctrl+v'), accelerator='Ctrl+V')
        self.right_click.add_command(label="Select All", command=lambda: keyboard.send('ctrl+a'), accelerator='Ctrl+A')

        def open_right_click(event):
            try:
                self.right_click.tk_popup(event.x_root, event.y_root)
            finally:
                self.right_click.grab_release()

        self.master.bind("<Button-3>", open_right_click)

        # Dropdown for selecting model
        self.model_selector = ttk.Combobox(self.main_frame, width=55, font='TkTextFont', state="readonly")
        self.model_selector.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        self.model_selector['values'] = ["gemini-pro", "gemini-pro-vision", "gpt-4-0125-preview",
                                         "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4-vision-preview",
                                         "gpt-3.5-turbo-1106", "gpt-3.5-turbo-16k", "gpt-3.5-turbo"]
        self.model_selector.current(0)

        # Button to clear chat
        self.clear_button = ttk.Button(self.main_frame, text="Clear Chat", width=12, command=self.clear_messages)
        self.clear_button.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="e")

        # Text area for chat messages
        self.chat_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, width=70, height=20,
                                                   font='TkTextFont',
                                                   state="disabled")
        self.chat_area.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Entry field for user input
        self.message_entry = ttk.Entry(self.main_frame, width=57, font='TkTextFont')
        self.message_entry.grid(row=2, column=0, padx=(10, 5), pady=(10, 0), sticky="w")

        # Button to send user message
        self.send_button = ttk.Button(self.main_frame, text="Send", width=12, command=self.send_message)
        self.send_button.grid(row=2, column=1, padx=(0, 10), pady=(10, 0), sticky="e")

        # Entry field for image directory
        self.image_directory = ttk.Entry(self.main_frame, width=57, font='TkTextFont', state="disabled")
        self.image_directory.grid(row=3, column=0, padx=(10, 5), pady=(5, 0), sticky="w")

        # Button to attach image
        self.attach_button = ttk.Button(self.main_frame, text="Attach", width=12, command=self.attach_image)
        self.attach_button.grid(row=3, column=1, padx=(0, 10), pady=(5, 0), sticky="e")

        # Label for status messages
        self.notice_label = tk.Label(self.main_frame, text=" ", fg="black", font='TkTextFont')
        self.notice_label.grid(row=4, column=0, padx=(10, 5), pady=(5, 10), sticky="w")

        # Button to show/hide API keys
        self.show_api_keys_button = ttk.Button(self.main_frame, text="API Keys...", width=12, command=self.show_api_keys)
        self.show_api_keys_button.grid(row=4, column=1, padx=(0, 10), pady=(5, 10), sticky="e")

        # Label and entry field for OpenAI API key
        self.openai_key_label = ttk.Label(self.api_keys_frame, text="OpenAI:", font='TkTextFont')
        self.openai_key_label.grid(row=0, column=0, padx=(10, 5), pady=(10, 5), sticky="w")

        self.openai_key_entry = ttk.Entry(self.api_keys_frame, show="*", width=50, font='TkTextFont')
        self.openai_key_entry.grid(row=0, column=1, padx=(0, 5), pady=(10, 5))

        self.show_openai_key_button = ttk.Button(self.api_keys_frame, text="Show", width=12,
                                                 command=self.show_openai_key)
        self.show_openai_key_button.grid(row=0, column=2, padx=(0, 10), pady=(10, 5), sticky="e")

        # Label and entry field for Gemini API key
        self.gemini_key_label = ttk.Label(self.api_keys_frame, text="Gemini:", font='TkTextFont')
        self.gemini_key_label.grid(row=1, column=0, padx=(10, 5), pady=(0, 10), sticky="w")

        self.gemini_key_entry = ttk.Entry(self.api_keys_frame, show="*", width=50, font='TkTextFont')
        self.gemini_key_entry.grid(row=1, column=1, padx=(0, 5), pady=(0, 10))

        self.show_gemini_key_button = ttk.Button(self.api_keys_frame, text="Show", width=12,
                                                 command=self.show_gemini_key)
        self.show_gemini_key_button.grid(row=1, column=2, padx=(0, 10), pady=(0, 10), sticky="e")

    # Method to send user message
    def send_message(self):
        message = self.message_entry.get()
        gemini_models = ["gemini-pro", "gemini-pro-vision"]
        openai_models = ["gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview",
                         "gpt-4-vision-preview", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-16k",
                         "gpt-3.5-turbo"]

        if message:
            self.notice_label.configure(text=" ")
            model = self.model_selector.get()
            prompt = self.message_entry.get()
            image = self.image_directory.get()
            openai_key = self.openai_key_entry.get()
            gemini_key = self.gemini_key_entry.get()

            if model in openai_models and openai_key or model in gemini_models and gemini_key:
                if model in ["gemini-pro-vision"] and image:
                    gemini(gemini_key, model, prompt, image)
                elif model in ["gpt-4-vision-preview"] and image:
                    openai(openai_key, model, prompt, image)
                elif model in ["gemini-pro"]:
                    gemini(gemini_key, model, prompt, image)
                    if image:
                        self.notice_label.configure(text="Switch to a vision model to process images. Currently ignoring the image.", fg="#FF8B00")
                elif model in ["gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview",
                               "gpt-3.5-turbo-1106", "gpt-3.5-turbo-16k", "gpt-3.5-turbo"]:
                    openai(openai_key, model, prompt, image)
                    if image:
                        self.notice_label.configure(text="Switch to a vision model to process images. Currently ignoring the image.", fg="#FF8B00")
                else:
                    self.notice_label.configure(text=f"Attach an image to use {model} or switch to a text model.", fg="#FF4A4A")
                    return
            else:
                self.notice_label.configure(text=f"Add your API key to use {model} or switch to another model.", fg="#FF4A4A")
                return

            if response:
                self.chat_area.configure(state="normal")
                self.chat_area.insert(tk.END, f"You: {message}\n")
                if model in ["gemini-pro", "gemini-pro-vision"]:
                    show_model = model.replace("-", " ").title()
                    self.chat_area.insert(tk.END, f"{show_model}: {response.text}\n\n")
                else:
                    show_model = model.replace("-", " ").title().replace("Gpt", "GPT")
                    self.chat_area.insert(tk.END, f"{show_model}: {response}\n\n")
                self.chat_area.configure(state="disabled")

                self.message_entry.delete(0, tk.END)
                self.image_directory.configure(state="normal")
                self.image_directory.delete(0, tk.END)
                self.image_directory.configure(state="disabled")

        else:
            return

    # Method to attach image
    def attach_image(self):
        image = filedialog.askopenfilename(initialdir="/", title="Select an Image",
                                           filetypes=[("JPEG or PNG", ".jpg .png")])
        if image:
            self.image_directory.configure(state="normal")
            self.image_directory.delete(0, tk.END)
            self.image_directory.insert(tk.END, image)
            self.image_directory.configure(state="disabled")

    # Method to clear chat messages
    def clear_messages(self):
        self.chat_area.configure(state="normal")
        self.chat_area.delete('1.0', tk.END)
        self.chat_area.configure(state="disabled")

    # Method to show/hide API keys frame
    def show_api_keys(self):
        if self.show_api_keys_button.cget("text") == "API Keys...":
            self.api_keys_frame.grid(row=1, column=0)
            self.show_api_keys_button.configure(text=" API Keys... ")
        else:
            self.api_keys_frame.grid_forget()
            self.show_api_keys_button.configure(text="API Keys...")

    # Method to show/hide OpenAI API key
    def show_openai_key(self):
        if self.openai_key_entry.cget("show") == "*":
            self.openai_key_entry.configure(show="")
            self.show_openai_key_button.configure(text="Hide")
        else:
            self.openai_key_entry.configure(show="*")
            self.show_openai_key_button.configure(text="Show")

    # Method to show/hide Gemini API key
    def show_gemini_key(self):
        if self.gemini_key_entry.cget("show") == "*":
            self.gemini_key_entry.configure(show="")
            self.show_gemini_key_button.configure(text="Hide")
        else:
            self.gemini_key_entry.configure(show="*")
            self.show_gemini_key_button.configure(text="Show")

# Initialization
if __name__ == "__main__":
    root = ThemedTk(theme="breeze")
    app = Chatbot(root)
    root.mainloop()
