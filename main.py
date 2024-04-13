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
import subprocess
import json

PUBLIC_KEY = os.getenv('PUBLIC_KEY')
CLIENT_ID = os.getenv('CLIENT_ID')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

@app.route('/interactions', methods=['POST'])
@verify_key_decorator(PUBLIC_KEY)
def interactions():
    # JSONデータを取得
    data = request.json

    print(data)

    # インタラクションの種類を取得
    interaction_type = data["type"]

    # PINGの場合はPONGを返す
    if interaction_type == 1:
        response_ping = {"type": 1}
        requests.post(f"https://discord.com/api/v9/interactions/{data['id']}/{data['token']}/callback", json=response_ping, headers={"Authorization": f"Bot {DISCORD_TOKEN}", "Content-Type": "application/json"})

    # APPLICATION_COMMANDの場合は遅延レスポンスを返す
    elif interaction_type == 2:
        # 遅延レスポンスを返す
        response_data = {"type": 5}
        response = requests.post(f"https://discord.com/api/v9/interactions/{data['id']}/{data['token']}/callback", json=response_data, headers={"Authorization": f"Bot {DISCORD_TOKEN}", "Content-Type": "application/json"})
        
        command = data["data"]["name"]
        
        if command == "yt-ogp":
            ipturl = data["data"]["options"][0]["value"]
            media_type = data["data"]["options"][1]["value"]

            try:
                # yt-dlpを使用してURLを取得
                ydl_opts = {'format': 'best', 'no_cache': True}
                if media_type == 'audio':
                    ydl_opts['format'] = 'bestaudio'
                    ydl_opts['extract_audio'] = True

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(ipturl, download=False)
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
                            "url": video_url,
                            "color": 15548997,
                            "image": {"url": thumbnail},
                            "author": {"name": uploader, "url": uploader_url}
                        }

                        # メッセージを送信
                        message_data = {"embeds": [embed]}
                        headers = {
                            "Authorization": f"Bot {DISCORD_TOKEN}",
                            "Content-Type": "application/json"
                        }
                        requests.patch(f"https://discord.com/api/v9/webhooks/{CLIENT_ID}/{data['token']}/messages/@original", json=message_data, headers=headers)
                        return '', 200
            except Exception as e:
                print('Error processing interaction:', e)
                return 'Error processing interaction', 500
                
        if command == "yt-player":
            ipturl = data["data"]["options"][0]["value"]
            media_type = data["data"]["options"][1]["value"]
            
            try:
                # yt-dlpを使用してURLを取得
                ydl_opts = {'format': 'best', 'no_cache': True}
                if media_type == 'audio':
                    ydl_opts['format'] = 'bestaudio'
                    ydl_opts['extract_audio'] = True
        
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.extract_info(ipturl, download=False)
                    if 'url' in result:
                        media_url = result['url']
                        thumbnail = result.get('thumbnail')
                        title = result.get('title')
                        description = result.get('description', '')[:100]  # descriptionを取得し、最大100文字までに制限する
                        uploader = result.get('uploader')
                        uploader_url = result.get('uploader_url')
        
                        # Embedを作成
                        embed = {
                            "title": title,
                            "color": 15548997,
                            "author": {"name": uploader, "url": uploader_url}
                        }
                        
                        if media_type == 'video':
                            embed["video"] = {"url": media_url}
                        elif media_type == 'audio':
                            embed["audio"] = {"url": media_url}

                        cnlid = data[channel_id]
                        
                        # pl.pyをサブプロセスとして実行し、データを渡す
                        subprocess.run(["python", "./pl.py", embed , cnlid ])

                        return '', 200
            except Exception as e:
                print('Error processing interaction:', e)
                return 'Error processing interaction', 500
    return '', 200

@app.route('/register-commands', methods=['GET'])
def register_commands():
    print('Received command registration request')

    commands = [
        {
            "name": "yt-ogp",
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
        },
        {
            "name": "yt-player",
            "description": "Fetch playing from YouTube URL",
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
        if response.status_code == 200:
            print('Commands registered:', response.json())
            return 'Commands have been registered'
    except Exception as e:
        print('Error registering commands:', e)
        return 'Error registering commands', 500
    return '', 200

if __name__ == '__main__':
    app.run(debug=False)
