import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# / エンドポイントでのGETリクエストを処理する
@app.route('/', methods=['GET'])
def get_url():
    url = request.args.get('url')
    media_type = request.args.get('type')

    # yt-dlpの--get-urlオプションを使用してURLを取得するコマンドを作成
    command = "yt-dlp --get-url"
    
    # タイプが指定されていれば、適切なフォーマットオプションを追加する
    if media_type == 'audio':
        command += " -f bestaudio"
    elif media_type == 'video':
        command += " -f bestvideo"

    command += " " + url

    # コマンドを実行し、結果を取得
    result = os.popen(command).read().strip()

    # 結果をJSON形式で返す
    return jsonify({'url': result})

# /json エンドポイントでのGETリクエストを処理する
@app.route('/json', methods=['GET'])
def get_json_url():
    url = request.args.get('url')
    media_type = request.args.get('type')

    # yt-dlpの--get-urlオプションを使用してURLを取得するコマンドを作成
    command = "yt-dlp --get-url"
    
    # タイプが指定されていれば、適切なフォーマットオプションを追加する
    if media_type == 'audio':
        command += " -f bestaudio"
    elif media_type == 'video':
        command += " -f bestvideo"

    command += " " + url

    # コマンドを実行し、結果を取得
    result = os.popen(command).read().strip()

    # 結果をJSON形式で返す
    return jsonify({'url': result})

if __name__ == '__main__':
    app.run(debug=True)
