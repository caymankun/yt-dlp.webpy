const express = require('express');
const cors = require('cors');
const ytdl = require('ytdl-core');
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
            quality: 'highest',
            filter: mediaType === 'audio' ? 'audioonly' : 'videoandaudio',
            format: mediaType === 'audio' ? 'mp3' : 'mp4',
            cwd: tempDir,
        };

        const videoInfo = await ytdl.getInfo(mediaUrl);
        const videoTitle = videoInfo.videoDetails.title;
        const filePath = path.join(tempDir, `${videoTitle}.${options.format}`);

        await ytdl.downloadFromInfo(videoInfo, options);
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
