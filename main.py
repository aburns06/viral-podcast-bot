from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/')
def home():
    return "Viral Podcast Bot is Live!"

@app.route('/process', methods=['POST'])
def process_video():
    data = request.get_json()
    video_url = data.get("video_url")

    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    # This is placeholder logic — simulate success for now
    fake_clip_url = f"https://viral-podcast-bot.onrender.com/videos/fake_clip_{random.randint(1000,9999)}.mp4"
    caption = "🔥 Viral podcast clip of the day! #podcast #motivation #reels"

    return jsonify({
        "video_url": fake_clip_url,
        "caption": caption
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
