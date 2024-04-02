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
                'format': 'bestvideo+bestaudio',
                'outtmpl': os.path.join(temp_dir, '%(title)s.mp4'),
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
        pass
    elif request.method == 'POST':
        # POSTリクエストの処理
        data = request.get_json()
        media_url = data.get('url')
        media_type = data.get('type')
        file_path_or_error = download_media(media_url, media_type)
        if isinstance(file_path_or_error, str):
            # ダウンロード成功時の処理
            file_path = file_path_or_error
            response = make_response(send_file(file_path))
            response.headers['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'

            # ダウンロード後、一時ディレクトリを一定時間後に削除する
            def delayed_cleanup():
                time.sleep(600)  # 10分待機
                cleanup_temp_directory(temp_dir)

            temp_dir = os.path.dirname(file_path)
            cleanup_thread = threading.Thread(target=delayed_cleanup)
            cleanup_thread.start()

            return response
        else:
            # エラー発生時の処理
            return file_path_or_error

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

