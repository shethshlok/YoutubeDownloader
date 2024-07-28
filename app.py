from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from pytubefix import YouTube
import re
import os

app = Flask(__name__)

# Regex pattern for validating YouTube URLs
youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')

# Path to the Downloads directory
downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

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
            audio_path = audio_stream.download(output_path=downloads_path, filename=f'{safe_title}.mp4')
            return redirect(url_for('wait', filename=f'{safe_title}.mp4'))
        else:
            video_stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
            video_path = video_stream.download(output_path=downloads_path, filename=f'{safe_title}.mp4')
            return redirect(url_for('wait', filename=f'{safe_title}.mp4'))
    except Exception as e:
        return redirect(url_for('index', error=str(e)))

@app.route('/wait')
def wait():
    filename = request.args.get('filename')
    return render_template('wait.html', filename=filename)

@app.route('/download_status/<filename>')
def download_status(filename):
    file_path = os.path.join(downloads_path, filename)
    if os.path.exists(file_path):
        return jsonify(ready=True)
    return jsonify(ready=False)

@app.route('/serve/<filename>')
def serve_file(filename):
    file_path = os.path.join(downloads_path, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')