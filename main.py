import yt_dlp
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os
from discord_interactions import InteractionType, InteractionResponseType, verify_key_decorator

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


# beta api

import hmac
import hashlib

PUBLIC_KEY = os.getenv('PUBLIC_KEY')
CLIENT_ID = os.getenv('CLIENT_ID')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

def send_deferred_response(response_url, response_data):
    """Send a deferred response to the provided response URL."""
    headers = {
        "Content-Type": "application/json"
    }

@app.route('/interactions', methods=['POST'])
@verify_key_decorator(PUBLIC_KEY)
def interactions():
    interaction_type = request.json

    if interaction_type == InteractionType.PING:
        return jsonify({"type": InteractionResponseType.PONG}), 200

    elif interaction_type == InteractionType.APPLICATION_COMMAND:
        command = data["data"]["name"]
        
        if command == "yt":
            url = data["data"]["options"][0]["value"]
            media_type = data["data"]["options"][1]["value"]

            # 遅延チャンネルメッセージを送信
            response_data = {"type": InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE}
            send_deferred_response(data["response_url"], response_data)

            try:
                # yt-dlpを使用してURLを取得
                ydl_opts = {'format': 'best', 'no_cache': True}
                if media_type == 'audio':
                    ydl_opts['format'] = 'bestaudio'
                    ydl_opts['extract_audio'] = True

                with YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(url, download=False)
                    if 'url' in result:
                        video_url = result['url']
                        thumbnail = result.get('thumbnail')
                        title = result.get('title')
                        description = result.get('description', '')[:100]  # descriptionを取得し、最大100文字までに制限する
                        uploader = result.get('uploader')
                        uploader_url = result.get('uploader_url')

                        # Embedを作成
                        embed = {
                            "type": "link",
                            "title": title,
                            "description": description,
                            "url": url,
                            "color": 0x0000FF,
                            "image": {"url": thumbnail},
                            "author": {"name": uploader, "url": uploader_url}
                        }

                        if media_type == 'video':
                            embed["video"] = {"url": video_url}
                        elif media_type == 'audio':
                            embed["audio"] = {"url": video_url}

                        # メッセージを送信
                        message_data = {"embeds": [embed]}
                        headers = {
                            "Authorization": f"Bot {DISCORD_TOKEN}",
                            "Content-Type": "application/json"
                        }
                        # Send the actual response
                        message_data = {"content": "動画を取得しました"}  # Placeholder message
                        requests.post(interaction_data["response_url"], json=message_data)
                        return '', 200
        
                    except Exception as e:
                        error_message = f"動画の取得中にエラーが発生しました: {str(e)}"
                        error_response = {"content": error_message}
                        requests.post(interaction_data["response_url"], json=error_response)
                        return '', 200
        
            return '', 200
   
@app.route('/register-commands', methods=['GET'])
def register_commands():
    print('Received command registration request')

    commands = [
        {
            "name": "yt",
            "description": "Fetch information from YouTube URL",
            "options": [
                {
                    "name": "url",
                    "description": "YouTube URL",
                    "type": 3,
                    "required": True
                },
                {
                    "name": "type",
                    "description": "Type of content (video or audio)",
                    "type": 3,
                    "required": True,
                    "choices": [
                        {"name": "動画", "value": "video"},
                        {"name": "音楽", "value": "audio"}
                    ]
                }
            ]
        }
    ]

    try:
        response = requests.put(f"https://discord.com/api/v9/applications/{CLIENT_ID}/commands", json=commands, headers={"Authorization": f"Bot {DISCORD_TOKEN}", "Content-Type": "application/json"})
        print('Commands registered:', response.json())
        return 'Commands have been registered'
    except Exception as e:
        print('Error registering commands:', e)
        return 'Error registering commands', 500

if __name__ == '__main__':
    app.run(debug=False)
