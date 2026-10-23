# Green Player

Green Player is a desktop music player built with Python and PySide6. It can search YouTube through `yt-dlp`, download audio for playback, and manage a local library, queue, favorites, and playlists.

## Features

- Search for tracks on YouTube
- Download/cache audio for playback
- Playback through VLC
- Music queue and library
- Favorites and playlists
- Shuffle and repeat controls
- Interface language selection: Polish, English, Spanish, French, and German
- Local data and audio cache stored in `~/MusicPlayer/`

> **Note:** Some interface strings may not yet be translated in every language.

## Requirements

### Python packages

- Python 3.10 or newer
- PySide6
- python-vlc
- yt-dlp

### System dependencies (Linux)

- VLC and its `libVLC` libraries
- FFmpeg (used by `yt-dlp` to convert audio to MP3)
- A working desktop environment

## Install on Kali Linux / Debian

Update package lists and install system dependencies:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv vlc libvlc5 ffmpeg
```

Create and activate a virtual environment in the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install PySide6 python-vlc yt-dlp
```

If your distribution's Python blocks installing packages into a system environment, use the virtual environment commands above rather than forcing a system-wide pip installation.

## Run from source

Place `main.py` in the project folder, activate the virtual environment, then run:

```bash
python main.py
```

## Data and cache

Green Player stores its local data under:

```text
~/MusicPlayer/
├── data.json
├── cache/
└── covers/
```

The application creates these folders automatically. Back up this folder if you want to preserve your local library data, favorites, queue, playlists, and language setting.

## Troubleshooting

### VLC / libVLC error

Make sure VLC and its runtime libraries are installed:

```bash
sudo apt install -y vlc libvlc5
```

### Audio conversion fails

Install FFmpeg:

```bash
sudo apt install -y ffmpeg
```

### YouTube search or download fails

Update `yt-dlp` inside the active virtual environment:

```bash
python -m pip install --upgrade yt-dlp
```

YouTube may change its service, so search or download can occasionally stop working until `yt-dlp` is updated. Internet access is required for online search and downloads.

## Legal note

Use Green Player only for content you are allowed to access and download. Respect copyright and the terms of the services you use.

## License

No license is specified in this repository yet. Add a `LICENSE` file before distributing the project if you want others to have explicit permission to reuse, modify, or redistribute it.
