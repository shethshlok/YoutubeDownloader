from flask import Flask, render_template, request, redirect, url_for, send_file
from pytubefix import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
from io import BytesIO
import re
import tempfile

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
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_audio:
                audio_stream.download(output_path=temp_audio.name)
                temp_audio.seek(0)
                audio_clip = AudioFileClip(temp_audio.name)
                mp3_buffer = BytesIO()
                audio_clip.write_audiofile(mp3_buffer, format='mp3')
                mp3_buffer.seek(0)
            return send_file(mp3_buffer, as_attachment=True, download_name=f'{safe_title}.mp3')
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                video_stream = yt.streams.filter(adaptivfrom flask import Flask, render_template, request, redirect, url_for, send_file
from pytubefix import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
from io import BytesIO
import re
import tempfile
import os

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
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
                audio_stream.download(output_path=temp_audio_path)
            audio_clip = AudioFileClip(temp_audio_path)
            mp3_buffer = BytesIO()
            audio_clip.write_audiofile(mp3_buffer, format='mp3')
            mp3_buffer.seek(0)
            os.remove(temp_audio_path)  # Remove the temporary file after processing
            return send_file(mp3_buffer, as_attachment=True, download_name=f'{safe_title}.mp3')
        else:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
                temp_video_path = temp_video.name
                video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True, resolution=resolution).first()
                video_stream.download(output_path=temp_video_path)
            video_clip = VideoFileClip(temp_video_path)

            audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).first()
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_audio:
                temp_audio_path = temp_audio.name
                audio_stream.download(output_path=temp_audio_path)
            audio_clip = AudioFileClip(temp_audio_path)

            final_clip = video_clip.set_audio(audio_clip)
            output_buffer = BytesIO()
            final_clip.write_videofile(output_buffer, codec='libx264')
            output_buffer.seek(0)
            
            os.remove(temp_video_path)  # Remove the temporary file after processing
            os.remove(temp_audio_path)  # Remove the temporary file after processing
            return send_file(output_buffer, as_attachment=True, download_name=f'{safe_title}.mp4')
    except Exception as e:
        app.logger.error(f"Error during download: {e}")
        return redirect(url_for('index', error=str(e)))

if __name__ == '__main__':
    app.run(debug=True)e=True, file_extension='mp4', only_video=True, resolution=resolution).first()
                video_stream.download(output_path=temp_video.name)
                video_clip = VideoFileClip(temp_video.name)

                audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).first()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_audio:
                    audio_stream.download(output_path=temp_audio.name)
                    audio_clip = AudioFileClip(temp_audio.name)

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