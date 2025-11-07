<div align="center">
  <a href="https://pypi.org/project/extra-whisper" target="_blank"><img src="https://img.shields.io/pypi/v/extra-whisper?label=PyPI%20Version&color=limegreen" /></a>
  <a href="https://pypi.org/project/extra-whisper" target="_blank"><img src="https://img.shields.io/pypi/pyversions/extra-whisper?color=limegreen" /></a>
  <a href="https://github.com/mohammadmansour200/extra-whisper/blob/master/LICENSE" target="_blank"><img src="https://img.shields.io/pypi/l/extra-whisper?color=limegreen" /></a>
  <a href="https://pepy.tech/project/extra-whisper" target="_blank"><img src="https://static.pepy.tech/badge/extra-whisper" /></a>
  <a href="https://colab.research.google.com/github/mohammadmansour200/extra-whisper/blob/master/colab_notebook.ipynb" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" /></a>
</div>

`extra_whisper`: Extended [faster-whisper](https://github.com/SYSTRAN/faster-whisper) with remote media transcription

## Features

- 🎧 **Transcription** using faster-whisper
- 📥 **Media download** from URLs (e.g., YouTube) using `yt-dlp`
- ✅ Local + remote (URL) input support

## Get started

Download package:
> Requires Python 3.9+

```bash
pip install extra-whisper
```

## Usage

```bash
from extra_whisper.transcribe import extra_transcribe

extra_transcribe(
    files=[
        "https://www.youtube.com/watch?v=123",
        "local_audio.mp3"
    ],
    output_dir="outputs"
)

```