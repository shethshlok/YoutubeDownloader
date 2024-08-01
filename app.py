from flask import Flask, render_template, request, redirect, url_for, send_file
from pytubefix import YouTube
import re
import requests
from io import BytesIO

app = Flask(__name__)

# Regex pattern for validating YouTube URLs
youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    file_format = request.form['format']
    if not youtube_regex.match(url):
        return redirect(url_for('index', error="Invalid YouTube URL"))

    try:
        yt = YouTube(url)
        video_title = yt.title
        safe_title = "".join([c if c.isalnum() else "_" for c in video_title])  # Make the title filename-safe

        if file_format == 'mp3':
            audio_stream = yt.streams.filter(only_audio=True).first()
            download_url = audio_stream.url
        else:
            video_stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
            download_url = video_stream.url

        return redirect(url_for('serve_video', title=safe_title, video_url=download_url, format=file_format))
    except Exception as e:
        return redirect(url_for('index', error=str(e)))

@app.route('/serve_video')
def serve_video():
    title = request.args.get('title')
    video_url = request.args.get('video_url')
    file_format = request.args.get('format')

    response = requests.get(video_url)
    if response.status_code != 200:
        return redirect(url_for('index', error="Failed to download video"))

    file_data = BytesIO(response.content)
    return send_file(file_data, as_attachment=True, download_name=f"{title}.{file_format}")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')