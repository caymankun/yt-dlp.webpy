import os
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# / エンドポイントでのGETリクエストを処理する
@app.route('/', methods=['GET'])
def get_url():
    url = request.args.get('url')
    media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return "URL parameter is required", 400

    # タイプに応じてyt-dlpのオプションを設定
    if media_type == 'audio':
        command = "yt-dlp --get-url --audio-format mp3 " + url
    elif media_type == 'video':
        command = "yt-dlp --get-url " + url
    else:
        return "Invalid media type", 400

    # コマンドを実行してURLを取得
    result = os.popen(command).read().strip()

    # URLを返す
    return result

# /json エンドポイントでのGETリクエストを処理する
@app.route('/json', methods=['GET'])
def get_url_json():
    url = request.args.get('url')
    media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    # タイプに応じてyt-dlpのオプションを設定
    if media_type == 'audio':
        command = "yt-dlp --get-url --audio-format mp3 " + url
    elif media_type == 'video':
        command = "yt-dlp --get-url " + url
    else:
        return jsonify({"error": "Invalid media type"}), 400

    # コマンドを実行してURLを取得
    result = os.popen(command).read().strip()

    # URLをJSON形式で返す
    return jsonify({"url": result})

# /e エンドポイントでのGETリクエストを処理する
@app.route('/e', methods=['GET'])
def play_media():
    url = request.args.get('url')
    media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return "URL parameter is required", 400

    # タイプに応じてyt-dlpのオプションを設定
    if media_type == 'audio':
        command = "yt-dlp --audio-format mp3 -o - " + url
    elif media_type == 'video':
        command = "yt-dlp -o - " + url
    else:
        return "Invalid media type", 400

    # コマンドを実行してファイルをストリーミング再生
    return send_file(os.popen(command), mimetype='audio/mpeg' if media_type == 'audio' else 'video/mp4')

if __name__ == '__main__':
    app.run(debug=True)
