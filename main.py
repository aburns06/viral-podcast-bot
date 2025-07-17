from flask import Flask, request, jsonify
import os, subprocess, uuid, re
from faster_whisper import WhisperModel
import openai

app = Flask(__name__, static_folder="videos", static_url_path="/videos")
openai.api_key = os.getenv("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")
model = WhisperModel("base", compute_type="int8")

@app.route("/process", methods=["POST"])
def process():
    try:
        video_url = request.json["video_url"]
        vid = str(uuid.uuid4())
        in_file = f"{vid}.mp4"
        out_file = f"videos/{vid}_clip.mp4"
        os.makedirs("videos", exist_ok=True)
        subprocess.run(["yt-dlp", "-f", "best", "-o", in_file, video_url])
        segments, _ = model.transcribe(in_file)
        text = " ".join(seg.text for seg in segments)
        prompt = f"Suggest a 30-60 sec viral clip timestamps (start & end):\n\n{text[:4000]}"
        resp = openai.ChatCompletion.create(
            model="gpt-4", messages=[{"role": "user", "content": prompt}]
        )
        m = re.findall(r"(\d{1,2}:\d{2})", resp.choices[0].message.content)
        if len(m) < 2:
            return jsonify(error="Invalid timestamps")
        to_sec = lambda t: int(t.split(":")[0]) * 60 + int(t.split(":")[1])
        start, end = to_sec(m[0]), to_sec(m[1])
        duration = end - start
        subprocess.run([
            "ffmpeg", "-ss", str(start), "-i", in_file, "-t", str(duration),
            "-vf", "scale=1080:1920", "-c:v", "libx264", "-c:a", "aac", "-y", out_file
        ])
        url = request.url_root + out_file
        return jsonify(video_url=url, caption="🔥 Viral podcast clip!")
    except Exception as e:
        return jsonify(error=str(e))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
