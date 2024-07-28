from flask import Flask, render_template, request, redirect, url_for, send_file
from pytube import YouTube
from io import BytesIO
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
            audio_data = BytesIO()
            audio_stream.stream_to_buffer(audio_data)
            audio_data.seek(0)
            return send_file(audio_data, mimetype='audio/mp3', as_attachment=True, download_name=f'{safe_title}.mp3')
        else:
            video_stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
            video_data = BytesIO()
            video_stream.stream_to_buffer(video_data)
            video_data.seek(0)
            return send_file(video_data, mimetype='video/mp4', as_attachment=True, download_name=f'{safe_title}.mp4')
    except Exception as e:
        return redirect(url_for('index', error=str(e)))

@app.route('/wait/<filename>')
def wait(filename):
    return render_template('wait.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')