from flask import Flask, request, jsonify
import yt_dlp
import uuid
import os
import openai
import tempfile

# Set your OpenAI API key
openai.api_key = "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"

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.get_json()
        video_url = data.get('video_url')

        if not video_url:
            return jsonify({'error': 'Missing video_url'}), 400

        # Create a unique filename
        video_id = str(uuid.uuid4())
        audio_file = f"{video_id}.mp3"

        # Download audio with yt-dlp and cookies
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_file,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'cookiefile': 'www.youtube.com_cookies.txt',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # Transcribe audio using OpenAI Whisper
        with open(audio_file, "rb") as f:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )

        text = transcript.text

        # Generate a viral caption using GPT
        prompt = f"""Here’s a podcast transcript snippet:\n{text}\n\nWrite a short viral Instagram Reel caption that would get people to watch this video."""
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a viral Instagram caption writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )
        caption = response.choices[0].message.content.strip()

        # Clean up audio file
        os.remove(audio_file)

        return jsonify({
            'status': 'success',
            'video_url_received': video_url,
            'caption': caption,
            'transcript': text
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
