from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from datetime import datetime
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST'])
def download_media():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided in the request'}), 400

    media_url = data.get('url')
    media_type = data.get('type')  # 'audio' or 'video'

    if not media_url or not media_type:
        return jsonify({'error': 'URL or type parameter is missing'}), 400

    try:
        now = datetime.now()
        formatted_now = now.strftime('%Y%m%d%H%M%S')
        output_file_name = f'output_{formatted_now}'

        if media_type == 'audio':
            ydl_opts = {
                'format': '22',
                'outtmpl': f'/tmp/{output_file_name}.mp3',
                'embed-thumbnail': True,
                'add-metadata': True,
            }
        elif media_type == 'video':
            ydl_opts = {
                'format': '22',
                'outtmpl': f'/tmp/{output_file_name}.mp4',
                'embed-thumbnail': True,
            }
        else:
            return jsonify({'error': 'Invalid media type'}), 400

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([media_url])

        file_path = f'/tmp/{output_file_name}.{media_type}'

        # レスポンスを作成してファイルを送信
        response = make_response(send_file(file_path))
        response.headers['Content-Disposition'] = f'attachment; filename={output_file_name}.{media_type}'
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
