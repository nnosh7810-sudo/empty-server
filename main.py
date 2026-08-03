from flask import Flask, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

@app.route("/audio")
def audio():
    video_id = request.args.get("id")
    if not video_id:
        return "Missing id", 400

    url = f"https://youtube.com/watch?v={video_id}"
    filename = f"{uuid.uuid4()}.mp3"
    output_path = f"/tmp/{filename}"

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": "/tmp/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        real_file = None
        for f in os.listdir("/tmp"):
            if f.endswith(".mp3"):
                real_file = f"/tmp/{f}"
                break

        if not real_file:
            return "Failed to extract audio", 500

        return send_file(real_file, mimetype="audio/mpeg")

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
