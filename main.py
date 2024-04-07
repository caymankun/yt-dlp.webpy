import yt_dlp
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def get_url():
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url')
        media_type = data.get('type')
    else:
        url = request.args.get('url')
        media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return "URL parameter is required", 400

    # タイプに応じてyt-dlpのオプションを設定
    ydl_opts = {'format': 'best' ,'no_cache': True}
    if media_type == 'audio':
        ydl_opts['format'] = 'bestaudio'
        ydl_opts['extract_audio'] = True

    # yt-dlpを使用してURLを取得
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=False)
        if 'url' in result:
            media_url = result['url']
            # ファイルを直接返して、適切なContent-Typeを設定する
            return media_url
        else:
            return 'URL not found in result', 500

@app.route('/json', methods=['GET', 'POST'])
def get_url_json():
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url')
        media_type = data.get('type')
    else:
        url = request.args.get('url')
        media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    # タイプに応じてyt-dlpのオプションを設定
    ydl_opts = {'format': 'best' ,'no_cache': True}
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

@app.route('/ogp', methods=['GET'])
def get_ogp_json():
    url = request.args.get('url')
    media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    # タイプに応じてyt-dlpのオプションを設定
    ydl_opts = {'format': 'best', 'no_cache': True}
    if media_type == 'audio':
        ydl_opts['format'] = 'bestaudio'
        ydl_opts['extract_audio'] = True

    # yt-dlpを使用してURLを取得
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=False)
        if 'url' in result:
            video_url = result['url']
            thumbnail = result.get('thumbnail')
            title = result.get('title')
            description = result.get('description', '')[:100]  # descriptionを取得し、最大100文字までに制限する
            uploader = result.get('uploader')
            uploader_url = result.get('uploader_url')

            response_data = {
                "url": video_url,
                "thumbnail": thumbnail,
                "title": title,
                "description": description,
                "author": uploader,
                "mediatype": media_type,
                "author_url": uploader_url
            }
            return jsonify(response_data)
        else:
            return jsonify({"error": "URL not found in result"}), 500

@app.route('/e', methods=['GET', 'POST'])
def get_embedded_media():
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url')
        media_type = data.get('type')
    else:
        url = request.args.get('url')
        media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return "URL parameter is required", 400

    # タイプに応じてyt-dlpのオプションを設定
    ydl_opts = {'format': 'best' ,'no_cache': True}
    if media_type == 'audio':
        ydl_opts['format'] = 'bestaudio'
        ydl_opts['extract_audio'] = True

    # yt-dlpを使用してURLを取得
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=False)
        if 'url' in result:
            media_url = result['url']
            # HTMLを直接返す
            if media_type == 'audio':
                html_content = f"<audio controls><source src='{media_url}' type='audio/mpeg'></audio>"
            elif media_type == 'video':
                html_content = f"<video controls><source src='{media_url}' type='video/mp4'></video>"
            else:
                return "Unsupported media type", 400
            return html_content
        else:
            return 'URL not found in result', 500

if __name__ == '__main__':
    app.run(debug=False)
