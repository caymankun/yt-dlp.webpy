from flask import Flask, request, jsonify, send_file
import subprocess
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def download_media(video_url, format, output_format):
    try:
        # yt-dlpコマンドを実行して動画または音声のダウンロード
        command = ["yt-dlp", "--format", format, "--get-url", video_url]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        download_url = result.stdout.strip()

        # ダウンロードしたメディアを一時的なファイルに保存
        temp_filename = f"temp.{output_format}"
        subprocess.run(["yt-dlp", "--format", format, "--output", temp_filename, video_url], check=True)

        return temp_filename
    except subprocess.CalledProcessError as e:
        return None

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('video_url')
    format = request.args.get('format')
    output_format = request.args.get('output_format', 'mp4')  # デフォルトはmp4

    if not video_url or not format:
        return jsonify({"error": "video_urlとformatは必須です。"})

    # メディアのダウンロード
    temp_filename = download_media(video_url, format, output_format)

    if temp_filename:
        try:
            # ダウンロードしたメディアをユーザーに提供
            return send_file(temp_filename, as_attachment=True, download_name=f"download.{output_format}")
        finally:
            # 一時ファイルを削除
            os.remove(temp_filename)
    else:
        return jsonify({"error": "メディアのダウンロードに失敗しました。"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

