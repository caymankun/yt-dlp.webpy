import yt_dlp
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os
from discord_interactions import InteractionType, InteractionResponseType, verify_key

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

PUBLIC_KEY = os.getenv('PUBLIC_KEY')
CLIENT_ID = os.getenv('CLIENT_ID')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

@app.route('/interactions', methods=['POST'])
def interactions():
    data = request.json
if not verify_key(request.headers.get('X-Signature-Ed25519'), str(request.headers.get('X-Signature-Timestamp')), request.data, PUBLIC_KEY):
    return jsonify({"error": "Invalid request"}), 401

def verify_key(signature, timestamp, raw_body, client_public_key):
    """Verify the signature of a Discord interaction request."""
    # Convert timestamp to string
    timestamp_str = str(timestamp)

    # Concatenate timestamp and raw_body
    message = timestamp_str + raw_body.decode()

    # Calculate the signature of the concatenated string
    calculated_signature = hmac.new(
        client_public_key.encode(), msg=message.encode(), digestmod=hashlib.sha256
    ).hexdigest()

    # Compare the calculated signature with the provided signature
    return hmac.compare_digest(signature, calculated_signature)

    

    interaction_type = InteractionType(data["type"])

    if interaction_type == InteractionType.PING:
        return jsonify({"type": InteractionResponseType.PONG})

    elif interaction_type == InteractionType.APPLICATION_COMMAND:
        command = data["data"]["name"]
        
        if command == "yt":
            url = data["data"]["options"][0]["value"]
            media_type = data["data"]["options"][1]["value"]

            # レスポンスを送信
            response_data = {"type": InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE}
            requests.post(data["response_url"], json=response_data)

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
                        channel_id = data["channel_id"]
                        message_url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
                        requests.post(message_url, json=message_data, headers=headers)

                        return jsonify({"content": "動画を取得しました"})
                    else:
                        return jsonify({"content": "動画が見つかりませんでした"})
            except Exception as e:
                return jsonify({"content": f"動画の取得中にエラーが発生しました: {str(e)}"}), 500

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
