#!/bin/sh

# Download and install ffmpeg
echo "Downloading and installing ffmpeg..."
FFMPEG_DIR=".ffmpeg"
mkdir -p $FFMPEG_DIR
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-64bit-static.tar.xz | tar -xJ --strip-components=1 -C $FFMPEG_DIR
export PATH="$PWD/$FFMPEG_DIR:$PATH"
echo "ffmpeg installed successfully."