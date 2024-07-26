from flask import Flask, render_template, request, redirect, url_for, send_file
from pytubefix import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
from io import BytesIO
import re

app = Flask(__name__)

# Enable debug mode
app.debug = True

# Regex pattern for validating YouTube URLs
youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_resolutions', methods=['POST'])
def fetch_resolutions():
    url = request.form['url']
    if not youtube_regex.match(url):
        app.logger.error(f"Invalid YouTube URL: {url}")
        return redirect(url_for('index', error="Invalid YouTube URL"))

    try:
        yt = YouTube(url)
        streams = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc()
        resolutions = list(set(stream.resolution for stream in streams))
        resolutions.sort(key=lambda x: int(x[:-1]), reverse=True)
        return render_template('index.html', url=url, resolutions=resolutions)
    except Exception as e:
        app.logger.error(f"Error fetching resolutions: {e}")
        return redirect(url_for('index', error=str(e)))

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    resolution = request.form['resolution']
    format = request.form['format']
    if not youtube_regex.match(url):
        app.logger.error(f"Invalid YouTube URL: {url}")
        return redirect(url_for('index', error="Invalid YouTube URL"))

    try:
        yt = YouTube(url)
        video_title = yt.title
        safe_title = "".join([c if c.isalnum() else "_" for c in video_title])  # Make the title filename-safe

        if format == 'mp3':
            audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).first()
            audio_data = audio_stream.stream_to_buffer()
            audio_clip = AudioFileClip(BytesIO(audio_data))
            audio_buffer = BytesIO()
            audio_clip.write_audiofile(audio_buffer, format='mp3')
            audio_buffer.seek(0)
            return send_file(audio_buffer, as_attachment=True, download_name=f'{safe_title}.mp3')
        else:
            video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True, resolution=resolution).first()
            video_data = video_stream.stream_to_buffer()
            video_clip = VideoFileClip(BytesIO(video_data))

            audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).first()
            audio_data = audio_stream.stream_to_buffer()
            audio_clip = AudioFileClip(BytesIO(audio_data))

            final_clip = video_clip.set_audio(audio_clip)
            output_buffer = BytesIO()
            final_clip.write_videofile(output_buffer, codec='libx264')
            output_buffer.seek(0)
            
            return send_file(output_buffer, as_attachment=True, download_name=f'{safe_title}.mp4')
    except Exception as e:
        app.logger.error(f"Error during download: {e}")
        return redirect(url_for('index', error=str(e)))

if __name__ == '__main__':
    app.run(debug=True)