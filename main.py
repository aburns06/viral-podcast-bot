import os
import json
import subprocess
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from faster_whisper import WhisperModel
import openai

openai.api_key = os.getenv("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")

app = Flask(__name__)

def download_youtube_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'quiet': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "downloaded.mp3"

def transcribe_audio(audio_path):
    model = WhisperModel("base", compute_type="int8")
    segments, _ = model.transcribe(audio_path)
    transcript_text = " ".join([segment.text for segment in segments])
    return transcript_text

def get_best_moment(transcript_text):
    prompt = f"""
    From the following podcast transcript, identify the most viral 30-60 second moment — the one most likely to go viral as a reel. Return ONLY the start and end time (in seconds) and a compelling caption.

    Transcript:
    {transcript_text[:5000]}

    Format your response like this:
    {{
        "start": 123,
        "end": 165,
        "caption": "Quote or short summary for the clip"
    }}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        data = json.loads(response['choices'][0]['message']['content'])
        return data
    except Exception as e:
        print("Failed to parse GPT response:", e)
        return None

def clip_video(input_path, start, end, output_path):
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-ss', str(start),
        '-to', str(end),
        '-vf', 'scale=720:1280',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-y',
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@app.route("/process", methods=["POST"])
def process():
    data = request.json
    video_url = data.get("video_url")
    if not video_url:
        return jsonify({"error": "Missing video_url"}), 400

    audio_path = download_youtube_audio(video_url)
    transcript_text = transcribe_audio(audio_path)
    best_moment = get_best_moment(transcript_text)

    if not best_moment:
        return jsonify({"error": "Could not extract viral moment"}), 500

    start_time = best_moment['start']
    end_time = best_moment['end']
    caption = best_moment['caption']

    clip_video("downloaded.mp3", start_time, end_time, "clip.mp4")

    return jsonify({
        "status": "success",
        "video_url_received": video_url,
        "start_time": start_time,
        "end_time": end_time,
        "caption": caption
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
