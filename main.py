from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Viral Podcast Bot is Running"

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    video_url = data.get("video_url")
    if not video_url:
        return jsonify({"error": "Missing video_url"}), 400

    return jsonify({
        "video_url": f"Clipped version of: {video_url}",
        "caption": "🔥 Viral podcast clip!"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
# Triggering redeploy
