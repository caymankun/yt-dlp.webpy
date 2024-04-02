const express = require('express');
const cors = require('cors');
const ytDlp = require('yt-dlp');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(cors());

// 一時ディレクトリを作成する関数
const createTempDirectory = () => {
    const tempDir = path.join(__dirname, 'tmp', uuidv4());
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
            cwd: tempDir,
            output: '%(title)s.%(ext)s',
            ffmpeg_location: 'https://apis.caymankun.f5.si/cgi-bin/ffmpeg',
            embed_thumbnail: true,
            add_metadata: true,
        };

        if (mediaType === 'audio') {
            options.format = 'bestaudio/best';
            options.audioformat = 'mp3';
        } else if (mediaType === 'video') {
            options.format = 'bestvideo+bestaudio';
        } else {
            throw new Error('Invalid media type');
        }

        const result = await ytDlp(mediaUrl, options);

        // ダウンロードされたファイルのパスを取得
        const filePath = path.join(tempDir, result.files[0].filename);

        return filePath;
    } catch (error) {
        throw new Error(`Failed to download media: ${error}`);
    }
}

// GETリクエストの処理
app.get('/', async (req, res) => {
    const { url, type } = req.query;

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
