from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({'error': 'No video URL provided'}), 400

    # This is just for testing. Replace with real processing logic.
    return jsonify({
        'status': 'success',
        'video_url_received': video_url,
        'caption': 'Sample viral caption for Instagram'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
