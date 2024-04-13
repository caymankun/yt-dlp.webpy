import discord
import json
import os
import sys

# Discord Botのトークン
TOKEN = os.getenv('DISCORD_TOKEN')

# コマンドライン引数からembedデータを受け取る
embed_json = sys.argv[1]

# JSON形式の文字列をPythonの辞書に変換
embed_data = json.loads(embed_json)

# コマンドライン引数からembedデータを受け取る
cnlid_json = sys.argv[2]

# JSON形式の文字列をPythonの辞書に変換
cnlid = json.loads(cnlid_json)

# Discordクライアントを作成
client = discord.Client()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    
    # 埋め込みメッセージを作成
    embed = discord.Embed.from_dict(embed_data)
  
    # メッセージを送信するチャンネルのIDを指定
    cnlid = 
  
    # メッセージを送信
    channel = client.get_channel(cnlid)  # メッセージを送信するチャンネルのIDを指定
    await channel.send(embed=embed)

# Discordクライアントを起動
client.run(TOKEN)
