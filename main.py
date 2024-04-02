import os
import shutil
import time
import random
import string
import subprocess
import requests
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
                'x': True,
                'audioformat': 'mp3',
                'outtmpl': os.path.join(temp_dir, '%(title)s.mp3'),
                'embed-thumbnail': True,
                'add-metadata': True,
                'N': 20,
            }
        elif media_type == 'video':
            ydl_opts = {
                'format': 'bestvideo/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.mp4'),
                'embed-thumbnail': True,
                'add-metadata': True,
                'N': 20,
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

# ffmpegバイナリをダウンロードする関数
def download_ffmpeg_binary():
    try:
        ffmpeg_url = "https://apis.caymankun.f5.si/cgi-bin/ffmpeg"
        ffmpeg_path = "/bin/ffmpeg"  # ダウンロード先のパス
        response = requests.get(ffmpeg_url, stream=True)
        if response.status_code == 200:
            with open(ffmpeg_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            os.chmod(ffmpeg_path, 0o755)  # 実行権限を付与
            return ffmpeg_path
        else:
            return None
    except Exception as e:
        print(f"An error occurred while downloading ffmpeg binary: {e}")
        return None

# ffmpegバイナリをダウンロードするエンドポイント
@app.route('/install_ffmpeg', methods=['GET'])
def install_ffmpeg():
    ffmpeg_path = download_ffmpeg_binary()
    if ffmpeg_path:
        return jsonify({'success': f'ffmpeg binary downloaded and saved at {ffmpeg_path}'})
    else:
        return jsonify({'error': 'Failed to download ffmpeg binary'}), 500
    

@app.route('/', methods=['GET', 'POST'])
def handle_request():
    if request.method == 'GET':
        # GETリクエストの処理
        media_url = request.args.get('url')
        media_type = request.args.get('type')
        file_path_or_error = download_media(media_url, media_type)
        if isinstance(file_path_or_error, str):
            if media_type == 'audio':
                return send_audio_file_or_return_error(file_path_or_error)
            elif media_type == 'video':
                return send_video_file_or_return_error(file_path_or_error)
            else:
                return jsonify({'error': 'Invalid media type'}), 400
        else:
            return file_path_or_error
    elif request.method == 'POST':
        # POSTリクエストの処理
        data = request.get_json()
        media_url = data.get('url')
        media_type = data.get('type')
        file_path_or_error = download_media(media_url, media_type)
        if isinstance(file_path_or_error, str):
            if media_type == 'audio':
                return send_audio_file_or_return_error(file_path_or_error)
            elif media_type == 'video':
                return send_video_file_or_return_error(file_path_or_error)
            else:
                return jsonify({'error': 'Invalid media type'}), 400
        else:
            return file_path_or_error

def send_audio_file_or_return_error(file_path):
    if os.path.exists(file_path):  # ファイルが存在するか確認
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'Downloaded audio file not found'})

def send_video_file_or_return_error(file_path):
    if os.path.exists(file_path):  # ファイルが存在するか確認
        response = send_file(file_path)
        response.headers['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
        return response
    else:
        return jsonify({'error': 'Downloaded video file not found'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
