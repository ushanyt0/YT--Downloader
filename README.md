# YT Downloader

A small self-hosted web app for downloading videos and audio with [yt-dlp](https://github.com/yt-dlp/yt-dlp). It runs on your own Android phone (Termux) or computer and you use it from your browser.

## Features

- Video (MP4) or audio (MP3)
- Quality selection: 1080p / 720p / 480p / 360p, or 320k / 192k / 128k for audio
- Whole playlists (downloaded as a ZIP) and English subtitles
- Progress bar
- Languages: English, Sinhala, Tamil, Hindi
- The finished file is saved by your browser like a normal download

## Install (Termux on Android)

    pkg update && pkg upgrade
    pkg install python ffmpeg nodejs git
    pip install yt-dlp yt-dlp-ejs flask
    git clone https://github.com/ushanyt0/YT--Downloader.git
    cd YT--Downloader
    python app.py

Then open `http://127.0.0.1:5000` in your browser. Stop the server with `CTRL + C`.

Node.js is needed because YouTube requires a JavaScript runtime for some formats.

## Terminal version

`dl.py` is a simple menu-based version without the web page. Run `termux-setup-storage` once, then `python dl.py`.

## Sharing it with a friend (temporary)

    pkg install cloudflared
    cloudflared tunnel --url http://localhost:5000

This prints a temporary public link. Anyone with the link can download using your phone's internet and IP, so only share it with people you trust and stop it when you are done.

## Troubleshooting

- Downloads stopped working: `pip install -U yt-dlp yt-dlp-ejs`
- "Sign in to confirm you're not a bot": this usually happens on cloud servers because YouTube blocks datacenter IPs. Run the app on your own phone or home computer instead.
- Only one download can run at a time.

## Please note

Only download content you have the right to download, such as your own videos or Creative Commons content. Downloading other content may break YouTube's Terms of Service or copyright law. You are responsible for how you use this tool.
