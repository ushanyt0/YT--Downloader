import yt_dlp

DEFAULT_URL = "https://youtu.be/gwov8azLd2Q?si=0O47vcjsMwJBmP9_"

url = input("Link එක දාන්න (Enter = example link): ").strip() or DEFAULT_URL

print("\n1) Video\n2) Audio (MP3)")
mode = input("තෝරන්න (1/2): ").strip()

opts = {
    "outtmpl": "/storage/emulated/0/Download/%(title)s.%(ext)s",
    "js_runtimes": {"node": {}},
}

if mode == "2":
    print("\nAudio quality:\n1) High (320k)\n2) Medium (192k)\n3) Low (128k)")
    c = input("තෝරන්න: ").strip()
    q = {"1": "320", "2": "192", "3": "128"}.get(c, "192")
    opts.update({
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": q,
        }],
    })
else:
    print("\nVideo quality:\n1) 1080p\n2) 720p\n3) 480p\n4) 360p\n5) Best available")
    c = input("තෝරන්න: ").strip()
    h = {"1": 1080, "2": 720, "3": 480, "4": 360}.get(c)
    if h:
        fmt = f"bv*[height<={h}][ext=mp4]+ba[ext=m4a]/bv*[height<={h}]+ba/b[height<={h}]"
    else:
        fmt = "bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/b"
    opts.update({"format": fmt, "merge_output_format": "mp4"})

with yt_dlp.YoutubeDL(opts) as ydl:
    ydl.download([url])
