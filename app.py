from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
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

@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    file_format = data.get('format')

    if not youtube_regex.match(url):
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        yt = YouTube(url)
        video_title = yt.title
        safe_title = "".join([c if c.isalnum() else "_" for c in video_title])  # Make the title filename-safe

        if file_format == 'mp3':
            stream = yt.streams.filter(only_audio=True).first()
        else:
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        download_url = stream.url
        return jsonify({'download_url': download_url, 'filename': f"{safe_title}.{file_format}"})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proxy_download')
def proxy_download():
    download_url = request.args.get('download_url')
    filename = request.args.get('filename')

    response = requests.get(download_url, stream=True)
    response.raise_for_status()

    return send_file(
        BytesIO(response.content),
        as_attachment=True,
        download_name=filename,
        mimetype='video/mp4'
    )

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')