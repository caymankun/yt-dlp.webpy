from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
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
        if media_type == 'audio':
            ydl_opts = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'outtmpl': '/tmp/%(title)s.%(ext)s',
                'embed-thumbnail': True,
                'add-metadata': True,
            }
        elif media_type == 'video':
            ydl_opts = {
                'format': 'best',
                'outtmpl': '/tmp/%(title)s.%(ext)s',
                'embed-thumbnail': True,
                'add-metadata': True,
            }
        else:
            return jsonify({'error': 'Invalid media type'}), 400

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(media_url, download=True)
            file_path = ydl.prepare_filename(info)

        # ファイルが存在するか確認
        if os.path.exists(file_path):
            # レスポンスを作成してファイルを送信
            response = make_response(send_file(file_path))
            response.headers['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
        else:
            return jsonify({'error': 'Downloaded file does not exist'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
