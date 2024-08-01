from flask import Flask, render_template, request, jsonify, redirect, url_for
from pytubefix import YouTube
import re

app = Flask(__name__)

# Regex pattern for validating YouTube URLs
youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_url', methods=['POST'])
def fetch_url():
    data = request.get_json()
    url = data['url']
    file_format = data['format']
    if not youtube_regex.match(url):
        return "Invalid YouTube URL", 400

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

        return jsonify({"download_url": download_url, "title": safe_title})
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')