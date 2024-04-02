from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

def download_media(media_url, media_type):
    if not media_url or not media_type:
        return jsonify({'error': 'URL or type parameter is missing'}), 400

    try:
        if media_type == 'audio':
            ydl_opts = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'outtmpl': '/tmp/%(title)s.mp3',
                'embed-thumbnail': True,
                'add-metadata': True,
            }
        elif media_type == 'video':
            ydl_opts = {
                'format': 'best',
                'outtmpl': '/tmp/%(title)s.mp4',
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
            return file_path
        else:
            return jsonify({'error': 'Downloaded file does not exist'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    if request.method == 'GET':
        media_url = request.args.get('url')
        media_type = request.args.get('type')
        file_path_or_error = download_media(media_url, media_type)
        if isinstance(file_path_or_error, str):
            return send_file(file_path_or_error, as_attachment=True)
        else:
            return file_path_or_error
    elif request.method == 'POST':
        data = request.get_json()
        media_url = data.get('url')
        media_type = data.get('type')
        file_path_or_error = download_media(media_url, media_type)
        if isinstance(file_path_or_error, str):
            file_path = file_path_or_error
            response = make_response(send_file(file_path))
            response.headers['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
        else:
            return file_path_or_error

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
