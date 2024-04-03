import os
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# / エンドポイントでのGETリクエストを処理する
@app.route('/', methods=['GET'])
def get_url():
    url = request.args.get('url')

    # パラメーターがない場合はエラーメッセージを返す
    if not url:
        return "URL parameter is required", 400

    # yt-dlpの--get-urlオプションを使用してURLを取得するコマンドを作成
    command = "yt-dlp --get-url " + url

    # コマンドを実行し、結果を取得
    result = os.popen(command).read().strip()

    # 結果を返す
    return result

# /json エンドポイントでのGETリクエストを処理する
@app.route('/json', methods=['GET'])
def get_json_url():
    url = request.args.get('url')

    # パラメーターがない場合はエラーメッセージを返す
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400

    # yt-dlpの--get-urlオプションを使用してURLを取得するコマンドを作成
    command = "yt-dlp --get-url " + url

    # コマンドを実行し、結果を取得
    result = os.popen(command).read().strip()

    # 結果をJSON形式で返す
    return jsonify({'url': result})

if __name__ == '__main__':
    app.run(debug=True)
