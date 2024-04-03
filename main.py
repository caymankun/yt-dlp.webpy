import yt_dlp
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def get_url():
    url = request.args.get('url')
    media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return "URL parameter is required", 400

    # タイプに応じてyt-dlpのオプションを設定
    ydl_opts = {'format': 'best'}
    if media_type == 'audio':
        ydl_opts['format'] = 'bestaudio'
        ydl_opts['extract_audio'] = True

    # yt-dlpを使用してURLを取得
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=False)
        if 'url' in result:
            media_url = result['url']
            # URLを直接返して、適切なContent-Typeを設定する
            return send_file(media_url, mimetype=media_type)
        else:
            return 'URL not found in result', 500

@app.route('/json', methods=['GET'])
def get_url_json():
    url = request.args.get('url')
    media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    # タイプに応じてyt-dlpのオプションを設定
    ydl_opts = {'format': 'best'}
    if media_type == 'audio':
        ydl_opts['format'] = 'bestaudio'
        ydl_opts['extract_audio'] = True

    # yt-dlpを使用してURLを取得
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=False)
        if 'url' in result:
            return jsonify({"url": result['url']})
        else:
            return jsonify({"error": "URL not found in result"}), 500

@app.route('/e', methods=['GET'])
def play_media():
    url = request.args.get('url')
    media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return "URL parameter is required", 400

    # タイプに応じてyt-dlpのオプションを設定
    ydl_opts = {'format': 'best'}
    if media_type == 'audio':
        ydl_opts['format'] = 'bestaudio'
        ydl_opts['extract_audio'] = True

    # yt-dlpを使用してURLを取得
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=False)
        if 'url' in result:
            media_url = result['url']
            # URLを直接返して、適切なContent-Typeを設定する
            return send_file(media_url, mimetype=media_type)
        else:
            return 'URL not found in result', 500


if __name__ == '__main__':
    app.run(debug=True)
