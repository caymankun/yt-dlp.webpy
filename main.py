import os
import shutil
import random
import string
import subprocess
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# 一時ディレクトリを作成する関数
def create_temp_directory():
    temp_dir = '/tmp/' + ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    os.makedirs(temp_dir)
    return temp_dir

# 一時ディレクトリを削除する関数
def cleanup_temp_directory(temp_dir):
    shutil.rmtree(temp_dir)

# ffmpegのパスを設定する関数
def set_ffmpeg_path():
    ffmpeg_path = 'https://apis.caymankun.f5.si/cgi-bin/ffmpeg'  # ffmpegのバイナリのパスを設定
    os.environ['PATH'] += os.pathsep + os.path.dirname(ffmpeg_path)

# 動画または音声をダウンロードする関数
def download_media(media_url, media_type):
    temp_dir = create_temp_directory()  # 一時ディレクトリを作成

    try:
        file_path = os.path.join(temp_dir, 'media')  # ファイル名はそのままにする
        # yt-dlpのコマンドをsubprocessで実行して動画または音声をダウンロード
        subprocess.run(['yt-dlp', '--format', 'bestvideo+bestaudio' if media_type == 'video' else 'bestaudio', '-o', file_path, media_url], check=True)
        
        return file_path

    except subprocess.CalledProcessError as e:
        return str(e), 500
    except Exception as e:
        return str(e), 500

@app.route('/', methods=['GET'])
def handle_request():
    media_url = request.args.get('url')
    media_type = request.args.get('type')
    if not media_url or not media_type:
        return jsonify({'error': 'URL or type parameter is missing'}), 400

    file_path_or_error = download_media(media_url, media_type)
    if isinstance(file_path_or_error, str):
        return jsonify({'error': file_path_or_error}), 500
    else:
        return send_file(file_path_or_error)

if __name__ == '__main__':
    set_ffmpeg_path()
    app.run(host='0.0.0.0', port=8080)
