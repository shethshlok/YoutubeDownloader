# from pytubefix import YouTube
# from pytubefix.cli import on_progress
 
# url = "https://www.youtube.com/watch?v=TIQ5hrfermg"


# yt = YouTube(url, on_progress_callback = on_progress)

# streams = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc()

# # Extracting the resolutions
# resolutions = list(set(stream.resolution for stream in streams))

# # Sorting the resolutions for better readability
# resolutions.sort(key=lambda x: int(x[:-1]), reverse=True)

# print(resolutions)

# RES = '1080p' # set what the user selects

# for idx,i in enumerate(yt.streams):
#    if i.resolution ==RES:
#       print(idx)
#       print(i.resolution)
#       break
# print(yt.streams[idx])
# yt.streams[idx].download()

import os
from pytubefix import YouTube
from pytubefix.cli import on_progress
from moviepy.editor import VideoFileClip, AudioFileClip

url = "https://www.youtube.com/watch?v=_G4vCAmgsUo"

yt = YouTube(url, on_progress_callback=on_progress)

# Get the title of the video
video_title = yt.title
safe_title = "".join([c if c.isalnum() else "_" for c in video_title])  # Make the title filename-safe

# Download video stream
video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
video_path = video_stream.download(filename=f'{safe_title}_video.mp4')

# Download audio stream
audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).first()
audio_path = audio_stream.download(filename=f'{safe_title}_audio.mp4')

# Merge video and audio using moviepy
video_clip = VideoFileClip(video_path)
audio_clip = AudioFileClip(audio_path)
final_clip = video_clip.set_audio(audio_clip)
output_path = f'{safe_title}.mp4'
final_clip.write_videofile(output_path, codec='libx264')

# Delete the separate video and audio files
os.remove(video_path)
os.remove(audio_path)

print(f"Video downloaded and merged successfully: {output_path}")

