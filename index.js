const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const { exec } = require('child_process');
const ytdlp = require('yt-dlp-wrap');

const app = express();
app.use(cors());

// 一時ディレクトリを作成する関数
const createTempDirectory = () => {
    const tempDir = path.join('/tmp', uuidv4());
    fs.mkdirSync(tempDir, { recursive: true });
    return tempDir;
}

// 一時ディレクトリを削除する関数
const cleanupTempDirectory = (tempDir) => {
    fs.rmdirSync(tempDir, { recursive: true });
}

// 動画をダウンロードする関数
const downloadMedia = async (mediaUrl, mediaType) => {
    const tempDir = createTempDirectory();

    try {
        const options = {
            format: mediaType === 'audio' ? 'bestaudio/best' : 'bestvideo+bestaudio',
            output: path.join(tempDir, '%(title)s.%(ext)s'),
            embedThumbnail: true,
            addMetadata: true,
            noPlaylist: true,
        };

        await ytdlp.download(mediaUrl, options);

        // ダウンロードされたファイルのパスを取得
        const files = fs.readdirSync(tempDir);
        const filePath = path.join(tempDir, files[0]);

        return filePath;
    } catch (error) {
        throw new Error(`Failed to download media: ${error}`);
    }
}

// GETリクエストの処理
app.get('/', async (req, res) => {
    const { url, type } = req.query;

    if (!url || !type || (type !== 'audio' && type !== 'video')) {
        return res.status(400).json({ error: 'Invalid or missing parameters. Please specify "url" and "type" as either "audio" or "video".' });
    }

    try {
        const filePath = await downloadMedia(url, type);
        res.download(filePath, () => {
            cleanupTempDirectory(path.dirname(filePath));
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// サーバーを起動
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
