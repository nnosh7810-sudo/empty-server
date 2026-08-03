from flask import Flask, request, send_file
import aiohttp
import os
import uuid

app = Flask(__name__)

@app.route("/")
def home():
    return "✔ Server is running"

@app.route("/audio")
async def audio():
    video_id = request.args.get("id")
    if not video_id:
        return "Missing id", 400

    api = f"https://pipedapi.kavin.rocks/streams/{video_id}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api) as resp:
                if resp.status != 200:
                    return "Failed to fetch metadata", 500

                data = await resp.json()

        audio_streams = data.get("audioStreams", [])
        if not audio_streams:
            return "No audio streams found", 500

        best_audio = max(audio_streams, key=lambda x: x.get("bitrate", 0))
        audio_url = best_audio.get("url")

        if not audio_url:
            return "Audio URL missing", 500

        async with aiohttp.ClientSession() as session:
            async with session.get(audio_url) as resp:
                if resp.status != 200:
                    return "Failed to download audio", 500

                audio_data = await resp.read()

        filename = f"/tmp/{uuid.uuid4()}.webm"
        with open(filename, "wb") as f:
            f.write(audio_data)

        return send_file(filename, mimetype="audio/webm")

    except Exception as e:
        return str(e), 500
