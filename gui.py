import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from downloader import download_mp3, get_video_info
from PIL import Image, ImageTk
import io
import requests
import configparser


DARK_MODE = {
    "bg": "#2E2E2E",
    "fg": "#FFFFFF",
    "input_bg": "#424242",
    "input_fg": "#FFFFFF",
    "button_bg": "#4A4A4A",
    "button_fg": "#FFFFFF",
    "highlight_bg": "#4A4A4A",
    "highlight_fg": "#FFFFFF"
}

LIGHT_MODE = {
    "bg": "#FFFFFF",
    "fg": "#000000",
    "input_bg": "#FFFFFF",
    "input_fg": "#000000",
    "button_bg": "#E0E0E0",
    "button_fg": "#000000",
    "highlight_bg": "#D6D6D6",
    "highlight_fg": "#000000"
}



class YouTubeDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("YouTube MP3 Downloader")

        self.url_label = tk.Label(master, text="YouTube URL:")
        self.url_label.pack()

        self.url_entry = tk.Entry(master, width=50)
        self.url_entry.pack()
        self.url_entry.bind("<FocusOut>", self.show_video_info)

        self.path_label = tk.Label(master, text="Download Path:")
        self.path_label.pack()

        self.path_entry = tk.Entry(master, width=50)
        self.path_entry.pack()
        path, _ = self.load_settings()
        self.path_entry.insert(0, path)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse)
        self.browse_button.pack()

        self.download_button = tk.Button(master, text="Download", command=self.start_download_thread)
        self.download_button.pack()
        
        self.progress = ttk.Progressbar(master, mode='determinate')
        self.progress.pack()

        self.status_label = tk.Label(master, text="Status: Ready")
        self.status_label.pack()

        # Add these before the theme is applied
        self.title_label = tk.Label(master, text="Title:")
        self.title_label.pack()

        self.duration_label = tk.Label(master, text="Duration:")
        self.duration_label.pack()

        self.thumbnail_label = tk.Label(master)
        self.thumbnail_label.pack()

        # Now apply the theme
        self.theme_toggle = tk.Button(master, text="Toggle Dark Mode", command=self.toggle_theme)
        self.theme_toggle.pack()
        _, theme = self.load_settings()
        if theme == 'dark':
            self.apply_theme(DARK_MODE)



    def browse(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_selected)
            self.save_download_path(folder_selected)

    def start_download_thread(self):
        threading.Thread(target=self.download).start()

    def download(self):
        youtube_url = self.url_entry.get()
        download_path = self.path_entry.get()
        self.status_label.config(text="Status: Downloading...")
        download_mp3(youtube_url, download_path, self.update_progress)
        self.status_label.config(text="Status: Download Complete!")

    def update_progress(self, percent, eta):
        self.progress['value'] = percent
        self.status_label.config(text=f"Status: Downloading... {eta} remaining")

    def show_video_info(self, event=None):
        youtube_url = self.url_entry.get()
        try:
            info = get_video_info(youtube_url)
            self.title_label.config(text=f"Title: {info['title']}")
            self.duration_label.config(text=f"Duration: {info['duration']}s")

            thumbnail_image = Image.open(io.BytesIO(requests.get(info['thumbnail']).content))
            thumbnail_image.thumbnail((100, 100), Image.ANTIALIAS)
            self.thumbnail_photo = ImageTk.PhotoImage(thumbnail_image)
            self.thumbnail_label.config(image=self.thumbnail_photo)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch video info: {str(e)}")

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        path = config.get('Settings', 'download_path', fallback="~/Downloads/")
        theme = config.get('Settings', 'theme', fallback="light")
        return path, theme


    def save_settings(self, path=None, theme=None):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        if not config.has_section('Settings'):
            config.add_section('Settings')
        
        if path:
            config.set('Settings', 'download_path', path)
        if theme:
            config.set('Settings', 'theme', theme)

        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

    
    def toggle_theme(self):
        current_bg = self.master.cget("bg")
        if current_bg == LIGHT_MODE["bg"]:
            self.apply_theme(DARK_MODE)
            self.save_theme('dark')
        else:
            self.apply_theme(LIGHT_MODE)
            self.save_theme('light')

    def apply_theme(self, theme):
        widgets = [self.master, self.url_label, self.path_label, self.status_label, self.title_label, self.duration_label]
        for widget in widgets:
            widget.config(bg=theme["bg"])
            if widget != self.master:  # Exclude the main window when setting fg
                widget.config(fg=theme["fg"])

        # Separate configuration for the thumbnail_label since it doesn't support fg attribute
        self.thumbnail_label.config(bg=theme["bg"])

        self.url_entry.config(bg=theme["input_bg"], fg=theme["input_fg"], insertbackground=theme["fg"])
        self.path_entry.config(bg=theme["input_bg"], fg=theme["input_fg"], insertbackground=theme["fg"])

        self.browse_button.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["highlight_bg"], activeforeground=theme["highlight_fg"])
        self.download_button.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["highlight_bg"], activeforeground=theme["highlight_fg"])
        self.theme_toggle.config(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["highlight_bg"], activeforeground=theme["highlight_fg"])


    def save_theme(self, theme):
        self.save_settings(theme=theme)


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
