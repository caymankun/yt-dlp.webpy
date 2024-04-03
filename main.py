import subprocess
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_url():
    url = request.args.get('url')
    media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return "URL parameter is required", 400

    # タイプに応じてyt-dlpのオプションを設定
    ydl_opts = "--get-url"
    if media_type == 'audio':
        ydl_opts += " -x"  # 音声の場合は-xオプションを追加する

    # コマンドを実行してURLを取得
    result = subprocess.run(['yt-dlp', ydl_opts, url], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return result.stderr.strip(), 500

@app.route('/json', methods=['GET'])
def get_url_json():
    url = request.args.get('url')
    media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    # タイプに応じてyt-dlpのオプションを設定
    ydl_opts = "--get-url"
    if media_type == 'audio':
        ydl_opts += " -x"  # 音声の場合は-xオプションを追加する

    # コマンドを実行してURLを取得
    result = subprocess.run(['yt-dlp', ydl_opts, url], capture_output=True, text=True)
    if result.returncode == 0:
        return jsonify({"url": result.stdout.strip()})
    else:
        return jsonify({"error": result.stderr.strip()}), 500

@app.route('/echo', methods=['GET'])
def play_media():
    url = request.args.get('url')
    media_type = request.args.get('type')

    # URLパラメーターがない場合はエラーメッセージを返す
    if not url:
        return "URL parameter is required", 400

    # タイプに応じてyt-dlpのオプションを設定
    ydl_opts = "--get-url"
    if media_type == 'audio':
        ydl_opts += " -x"  # 音声の場合は-xオプションを追加する

    # コマンドを実行してURLを取得
    result = subprocess.run(['yt-dlp', ydl_opts, url], capture_output=True, text=True)
    if result.returncode == 0:
        media_url = result.stdout.strip()
        # URLを直接返して、適切なContent-Typeを設定する
        return send_file(media_url, mimetype=media_type)
    else:
        return result.stderr.strip(), 500

if __name__ == '__main__':
    app.run(debug=True)
