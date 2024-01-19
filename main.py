from flask_cors import CORS
from flask import Flask, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

def download_media(video_url, output_path, options):
    ydl_opts = {
        'outtmpl': f'{output_path}.%(ext)s',
        **options
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        media_file = ydl.prepare_filename(info)

    return f'{media_file}'

@app.route('/download', methods=['POST'])
def download_media_endpoint():
    # クエリパラメーターから動画URLとメディアの種類を取得
    video_url = request.args.get('url')
    media_type = request.args.get('type', 'audio')  # デフォルトは音声

    if not video_url:
        return jsonify({'error': 'Invalid request. "url" parameter is required.'}), 400

    try:
        # ダウンロード先のファイルパスを作成
        output_path = f"downloads/{media_type.capitalize()}/{os.path.basename(video_url)}"

        # yt-dlpを使用してメディアをダウンロード
        if media_type == 'video':
            options = {'format': 'bestvideo+bestaudio/best/mp4', 'merge_output_format': 'mp4', 'embed-thumbnail': True}
        elif media_type == 'audio':
            options = {'format': 'bestaudio/best', 'extractaudio': True, 'audioformat': 'mp3', 'embed-thumbnail': True, 'addmetadata': True}
        else:
            return jsonify({'error': 'Invalid media type. Supported types are "video" and "audio".'}), 400

        media_file = download_media(video_url, output_path, options)

        # ダウンロードしたメディアファイルをそのまま提供
        return send_file(media_file, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
