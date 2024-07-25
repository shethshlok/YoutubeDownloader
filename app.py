from flask import Flask, render_template, request, redirect, url_for
from pytubefix import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import re
import os

app = Flask(__name__)

# Regex pattern for validating YouTube URLs
youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')

# Path to the Downloads directory
downloads_path = '/tmp'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_resolutions', methods=['POST'])
def fetch_resolutions():
    url = request.form['url']
    if not youtube_regex.match(url):
        return redirect(url_for('index', error="Invalid YouTube URL"))

    try:
        yt = YouTube(url)
        streams = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc()
        resolutions = list(set(stream.resolution for stream in streams))
        resolutions.sort(key=lambda x: int(x[:-1]), reverse=True)
        return render_template('index.html', url=url, resolutions=resolutions)
    except Exception as e:
        return redirect(url_for('index', error=str(e)))

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    resolution = request.form['resolution']
    format = request.form['format']
    if not youtube_regex.match(url):
        return redirect(url_for('index', error="Invalid YouTube URL"))

    try:
        yt = YouTube(url)
        video_title = yt.title
        safe_title = "".join([c if c.isalnum() else "_" for c in video_title])  # Make the title filename-safe

        if format == 'mp3':
            audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).first()
            audio_path = audio_stream.download(output_path=downloads_path, filename=f'{safe_title}.mp4')
            # Convert to mp3 using moviepy
            audio_clip = AudioFileClip(audio_path)
            audio_clip.write_audiofile(os.path.join(downloads_path, f'{safe_title}.mp3'))
            os.remove(audio_path)
            return send_file(os.path.join(downloads_path, f'{safe_title}.mp3'), as_attachment=True)
        else:
            video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True, resolution=resolution).first()
            video_path = video_stream.download(output_path=downloads_path, filename=f'{safe_title}_video.mp4')
            audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).first()
            audio_path = audio_stream.download(output_path=downloads_path, filename=f'{safe_title}_audio.mp4')

            # Merge video and audio using moviepy
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            final_clip = video_clip.set_audio(audio_clip)
            output_path = os.path.join(downloads_path, f'{safe_title}.mp4')
            final_clip.write_videofile(output_path, codec='libx264')

            # Delete the separate video and audio files
            os.remove(video_path)
            os.remove(audio_path)

            return send_file(output_path, as_attachment=True)
    except Exception as e:
        return redirect(url_for('index', error=str(e)))

if __name__ == '__main__':
    app.run(debug=False)