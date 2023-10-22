import yt_dlp as youtube_dl
import os
import re

def hook(d, on_progress=None):
    if d['status'] == 'finished':
        if on_progress:
            on_progress(100, 'Converting...')
    if d['status'] == 'downloading':
        if on_progress:
            percent = re.sub(r'\x1b\[[0-9;]*m', '', d.get('_percent_str', '0%'))
            percent = percent.strip('% ').replace(',', '.')
            if not percent.replace('.', '').isdigit():
                percent = '0'
            eta = d.get('_eta_str', '0:00')
            on_progress(float(percent), eta)

def download_mp3(youtube_url, output_path='~/Downloads/', on_progress=None):
    options = {
        'format': 'bestaudio+bestvideo/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': os.path.expanduser(os.path.join(output_path, '%(title)s.%(ext)s')),
        'noplaylist': True,
        'progress_hooks': [lambda d: hook(d, on_progress)],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }, {
            'key': 'FFmpegMetadata',
        }],
    }

    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([youtube_url])

def get_video_info(youtube_url):
    with youtube_dl.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        return {
            'title': info_dict.get('title', ''),
            'thumbnail': info_dict.get('thumbnail', ''),
            'duration': info_dict.get('duration', 0)
        }
