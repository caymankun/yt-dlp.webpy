import os
import shutil
import random
import string
import subprocess
import requests
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# 一時ディレクトリを作成する関数
def create_temp_directory():
    temp_dir = '/tmp/' + ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    os.makedirs(temp_dir)
    return temp_dir

# yt-dlpとffmpegをダウンロードしてパスを通す関数
def setup():
    try:
        # yt-dlpをダウンロードして実行権限を付与
        yt_dlp_url = "https://apis.caymankun.f5.si/cgi-bin/yt-dlp"
        yt_dlp_path = "/usr/local/bin/yt-dlp"
        with requests.get(yt_dlp_url, stream=True) as r:
            with open(yt_dlp_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        os.chmod(yt_dlp_path, 0o755)  # 実行権限を付与

        # ffmpegをダウンロードしてパスを通す
        ffmpeg_url = "https://apis.caymankun.f5.si/cgi-bin/ffmpeg"
        ffmpeg_path = "/usr/local/bin/ffmpeg"
        with requests.get(ffmpeg_url, stream=True) as r:
            with open(ffmpeg_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        os.chmod(ffmpeg_path, 0o755)  # 実行権限を付与

        return True
    except Exception as e:
        print(f"An error occurred during setup: {e}")
        return False

# 動画または音声をダウンロードする関数
def download_media(media_url, media_type):
    temp_dir = create_temp_directory()  # 一時ディレクトリを作成

    try:
        if media_type == 'audio':
            command = f"yt-dlp --ffmpeg-location /usr/local/bin/ffmpeg --embed-thumbnail --add-metadata -x --audio-format mp3 -o '{temp_dir}/%(title)s.%(ext)s' {media_url}"
        elif media_type == 'video':
            command = f"yt-dlp --ffmpeg-location /usr/local/bin/ffmpeg --embed-thumbnail --add-metadata -f best -o '{temp_dir}/%(title)s.%(ext)s' {media_url}"
        else:
            return jsonify({'error': 'Invalid media type'}), 400

        subprocess.run(command, shell=True, check=True)

        # ダウンロードされたファイルのパスを取得
        file_path = os.path.join(temp_dir, os.listdir(temp_dir)[0])

        return file_path

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# メディアファイルをダウンロードしてクライアントに送信するエンドポイント
@app.route('/', methods=['GET'])
def handle_request():
    # GETリクエストの処理
    media_url = request.args.get('url')
    media_type = request.args.get('type')
    
    # yt-dlpとffmpegのセットアップ
    if not setup():
        return jsonify({'error': 'Failed to setup yt-dlp and ffmpeg'}), 500
    
    # メディアのダウンロード
    file_path_or_error = download_media(media_url, media_type)
    if isinstance(file_path_or_error, str):
        return send_file(file_path_or_error, as_attachment=True)
    else:
        return file_path_or_error

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

