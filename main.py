from flask import Flask, request, jsonify
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def embed_thumbnail_url(video_url, thumbnail_url):
    # 動画URLにサムネイルURLをクエリパラメータとして追加
    embedded_url = f"{video_url}?thumbnail={thumbnail_url}"
    return embedded_url

@app.route('/', methods=['POST'])
def download_video():
    if request.method == 'POST':
        video_url = request.form['video_url']
        format = "mp4"
        
        # サムネイルURLをリクエストから取得
        thumbnail_url = request.form.get('thumbnail_url', '')  # 'thumbnail_url' を取得
        
        try:
            # yt-dlpコマンドを実行してダウンロードURLを取得
            command = ["yt-dlp", "--format", format, "--get-url", video_url]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            download_url = result.stdout.strip()
            
            if download_url:
                # サムネイルを埋め込んだURLを生成
                embedded_url = embed_thumbnail_url(download_url, thumbnail_url)
                return jsonify({"download_url": download_url, "embedded_url": embedded_url})
            else:
                return jsonify({"error": "ダウンロードURLの取得に失敗しました。"})
        except subprocess.CalledProcessError as e:
            return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
