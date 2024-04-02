import os
import shutil
import time
import random
import string
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

# 一時ディレクトリを作成する関数
def create_temp_directory():
    temp_dir = '/tmp/' + ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    os.makedirs(temp_dir)
    return temp_dir

# 一時ディレクトリを削除する関数
def cleanup_temp_directory(temp_dir):
    shutil.rmtree(temp_dir)

# 動画をダウンロードする関数
def download_media(media_url, media_type):
    temp_dir = create_temp_directory()  # 一時ディレクトリを作成

    try:
        if media_type == 'audio':
            ydl_opts = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'outtmpl': os.path.join(temp_dir, '%(title)s.mp3'),
                'embed-thumbnail': True,
                'add-metadata': True,
            }
        elif media_type == 'video':
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.webm'),
                'embed-thumbnail': True,
                'add-metadata': True,
            }
        else:
            return jsonify({'error': 'Invalid media type'}), 400

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([media_url])

        # ダウンロードされたファイルのパスを取得
        file_path = os.path.join(temp_dir, os.listdir(temp_dir)[0])

        return file_path

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    if request.method == 'GET':
        # GETリクエストの処理
        media_url = request.args.get('url')
        media_type = request.args.get('type')
        file_path_or_error = download_media(media_url, media_type)
        if isinstance(file_path_or_error, str):
            return send_file_or_return_error(file_path_or_error, media_type)
        else:
            return file_path_or_error
    elif request.method == 'POST':
        # POSTリクエストの処理
        data = request.get_json()
        media_url = data.get('url')
        media_type = data.get('type')
        file_path_or_error = download_media(media_url, media_type)
        if isinstance(file_path_or_error, str):
            return send_file_or_return_error(file_path_or_error, media_type)
        else:
            return file_path_or_error

def send_file_or_return_error(file_path, media_type):
    if os.path.exists(file_path):  # ファイルが存在するか確認
        if media_type == 'video':
            return send_file(file_path, as_attachment=True)
        else:
            return send_file(file_path, as_attachment=True, attachment_filename=os.path.basename(file_path))
    else:
        return jsonify({'error': 'Downloaded file not found'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
