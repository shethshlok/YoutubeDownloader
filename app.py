from flask import Flask, render_template, request, redirect, url_for
from pytubefix import YouTube
import re

app = Flask(__name__)

# Regex pattern for validating YouTube URLs
youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format = request.form['format']
    if not youtube_regex.match(url):
        return redirect(url_for('index', error="Invalid YouTube URL"))

    try:
        yt = YouTube(url)
        video_title = yt.title
        safe_title = "".join([c if c.isalnum() else "_" for c in video_title])  # Make the title filename-safe

        if format == 'mp3':
            audio_stream = yt.streams.filter(only_audio=True).first()
            download_url = audio_stream.url
        else:
            video_stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
            download_url = video_stream.url

        return redirect(download_url)
    except Exception as e:
        return redirect(url_for('index', error=str(e)))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')