
from flask import Flask, request, render_template_string, send_from_directory
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

FFMPEG_LOCATION = (
    r"C:\Users\aqeel\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-9.0.1-full_build\bin"
)

videos = {}


HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>TikSave</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f5f5f5;
    color: #222;
}

header {
    background: white;
    padding: 20px 8%;
    border-bottom: 1px solid #eee;
}

.logo {
    font-size: 28px;
    font-weight: bold;
}

.container {
    max-width: 850px;
    margin: 60px auto;
    padding: 20px;
    text-align: center;
}

h1 {
    font-size: 44px;
    margin-bottom: 10px;
}

.subtitle {
    color: #777;
    margin-bottom: 30px;
}

.form {
    background: white;
    padding: 10px;
    border-radius: 14px;
    display: flex;
    gap: 10px;
    box-shadow: 0 8px 30px rgba(0,0,0,.08);
}

input {
    flex: 1;
    padding: 18px;
    border: 0;
    outline: none;
    font-size: 16px;
    direction: ltr;
}

button {
    background: #111;
    color: white;
    border: 0;
    border-radius: 10px;
    padding: 0 30px;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    opacity: .88;
}

.preview {
    background: white;
    margin-top: 30px;
    padding: 25px;
    border-radius: 15px;
}

.preview img {
    width: 100%;
    max-width: 400px;
    border-radius: 12px;
}

.title {
    font-size: 20px;
    font-weight: bold;
    margin: 20px 0;
}

.quality {
    max-width: 350px;
    margin: 20px auto;
    text-align: right;
}

.quality label {
    display: block;
    font-weight: bold;
    margin-bottom: 8px;
}

select {
    width: 100%;
    padding: 14px;
    border: 1px solid #ddd;
    border-radius: 10px;
    background: white;
    font-size: 16px;
}

.buttons {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 20px;
}

.download {
    display: inline-block;
    background: #111;
    color: white;
    text-decoration: none;
    padding: 15px 25px;
    border-radius: 10px;
}

.audio {
    background: #444;
}

.new-video {
    display: inline-block;
    margin-top: 15px;
    padding: 14px 25px;
    border-radius: 10px;
    background: #e8e8e8;
    color: #111;
    text-decoration: none;
}

.error {
    background: #ffe5e5;
    color: #a00000;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.ad {
    margin-top: 50px;
    height: 90px;
    background: #e8e8e8;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #999;
    border-radius: 8px;
}

@media (max-width: 600px) {

    .container {
        margin-top: 35px;
    }

    h1 {
        font-size: 32px;
    }

    .form {
        flex-direction: column;
    }

    input {
        width: 100%;
    }

    button {
        height: 55px;
    }

    .download,
    .new-video {
        width: 100%;
    }
}

</style>

</head>

<body>

<header>
    <div class="logo">TikSave</div>
</header>

<div class="container">

    <h1>تحميل فيديو TikTok</h1>

    <div class="subtitle">
        الصق رابط TikTok لتحميل الفيديو
    </div>

    {% if error %}

        <div class="error">
            {{ error }}
        </div>

    {% endif %}

    <form method="POST" class="form">

        <input
            type="url"
            name="url"
            placeholder="https://www.tiktok.com/..."
            value="{{ url }}"
            required
        >

        <button type="submit">
            معاينة
        </button>

    </form>

    {% if video %}

        <div class="preview">

            {% if video.thumbnail %}

                <img
                    src="{{ video.thumbnail }}"
                    alt="TikTok thumbnail"
                >

            {% endif %}

            <div class="title">
                {{ video.title }}
            </div>

            <p>
                مدة الفيديو: {{ video.duration }}
            </p>

            <div class="quality">

                <label for="quality">
                    جودة الفيديو
                </label>

                <select id="quality">

                    <option value="1080">
                        1080p — الأفضل
                    </option>

                    <option value="720">
                        720p
                    </option>

                    <option value="480">
                        480p
                    </option>

                    <option value="360">
                        360p
                    </option>

                    <option value="best">
                        أعلى جودة متاحة
                    </option>

                </select>

            </div>

            <div class="buttons">

                <a
                    id="downloadButton"
                    class="download"
                    href="/download/{{ video.id }}?quality=1080"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    ⬇ تحميل MP4
                </a>

                <a
                    class="download audio"
                    href="/audio/{{ video.id }}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    🎵 تحميل MP3
                </a>

            </div>

            <a
                class="new-video"
                href="/"
            >
                ➕ تحميل فيديو آخر
            </a>

        </div>

        <script>

        const qualitySelect =
            document.getElementById("quality");

        const downloadButton =
            document.getElementById("downloadButton");

        qualitySelect.addEventListener(
            "change",
            function () {

                downloadButton.href =
                    "/download/{{ video.id }}?quality=" +
                    this.value;

            }
        );

        </script>

    {% endif %}

    <div class="ad">
        مساحة إعلانية
    </div>

</div>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():

    error = None
    video = None
    url = ""

    if request.method == "POST":

        url = request.form.get("url", "").strip()

        if not url:

            error = "أدخل رابط TikTok."

        elif "tiktok.com" not in url:

            error = "الرابط يجب أن يكون من TikTok."

        else:

            try:

                options = {
                    "quiet": True,
                    "no_warnings": True,
                    "noplaylist": True,
                    "retries": 8,
                    "fragment_retries": 8,
                    "extractor_retries": 3,
                    "socket_timeout": 30
                }

                with yt_dlp.YoutubeDL(options) as ydl:

                    info = ydl.extract_info(
                        url,
                        download=False
                    )

                video_id = str(uuid.uuid4())

                videos[video_id] = {
                    "url": url,
                    "title": info.get(
                        "title",
                        "TikTok Video"
                    )
                }

                duration = info.get("duration")

                if duration:
                    duration = f"{int(duration)} ثانية"
                else:
                    duration = "غير معروف"

                video = {
                    "id": video_id,
                    "title": info.get(
                        "title",
                        "TikTok Video"
                    ),
                    "thumbnail": info.get(
                        "thumbnail"
                    ),
                    "duration": duration
                }

            except Exception as e:

                print("PREVIEW ERROR:", e)

                error = (
                    "تعذر الحصول على معلومات الفيديو."
                )

    return render_template_string(
        HTML,
        error=error,
        video=video,
        url=url
    )


@app.route("/download/<video_id>")
def download(video_id):

    if video_id not in videos:
        return "الرابط غير موجود", 404

    data = videos[video_id]

    quality = request.args.get(
        "quality",
        "1080"
    )

    allowed_quality = [
        "1080",
        "720",
        "480",
        "360",
        "best"
    ]

    if quality not in allowed_quality:
        quality = "1080"

    filename = (
        video_id
        + "_"
        + quality
        + ".mp4"
    )

    output = os.path.join(
        DOWNLOAD_FOLDER,
        filename
    )

    if not os.path.exists(output):

        if quality == "best":

            # Prefer a single ready-to-download format to avoid
            # an unnecessary video+audio merge.
            format_option = (
                "best/"
                "bestvideo+bestaudio"
            )

        else:

            # Prefer a progressive format at or below the requested
            # height. If unavailable, merge separate video+audio.
            format_option = (
                f"best[height<={quality}]"
                f"/bestvideo[height<={quality}]"
                f"+bestaudio"
                f"/best[height<={quality}]"
                "/best"
            )

        options = {
            "outtmpl": output,
            "format": format_option,
            "merge_output_format": "mp4",
            "noplaylist": True,

            # More resilient network settings.
            "retries": 12,
            "fragment_retries": 12,
            "extractor_retries": 3,
            "file_access_retries": 3,
            "socket_timeout": 30,

            # Use a few concurrent fragments when the extractor
            # exposes fragmented media.
            "concurrent_fragment_downloads": 4,

            "continuedl": True,
            "nopart": False,

            "ffmpeg_location": FFMPEG_LOCATION
        }

        try:

            with yt_dlp.YoutubeDL(options) as ydl:

                ydl.download(
                    [data["url"]]
                )

        except Exception as e:

            print("DOWNLOAD ERROR:", e)

            return (
                "تعذر تحميل الفيديو. "
                "جرّب جودة أقل أو أعلى جودة متاحة.",
                500
            )

    return send_from_directory(
        DOWNLOAD_FOLDER,
        filename,
        as_attachment=True
    )


@app.route("/audio/<video_id>")
def audio(video_id):

    if video_id not in videos:
        return "الرابط غير موجود", 404

    data = videos[video_id]

    filename = video_id + ".mp3"

    output = os.path.join(
        DOWNLOAD_FOLDER,
        filename
    )

    if not os.path.exists(output):

        options = {
            "format": "bestaudio/best",
            "outtmpl": output,
            "noplaylist": True,
            "retries": 12,
            "fragment_retries": 12,
            "extractor_retries": 3,
            "file_access_retries": 3,
            "socket_timeout": 30,
            "concurrent_fragment_downloads": 4,
            "continuedl": True,
            "ffmpeg_location": FFMPEG_LOCATION,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192"
                }
            ]
        }

        try:

            with yt_dlp.YoutubeDL(options) as ydl:

                ydl.download(
                    [data["url"]]
                )

        except Exception as e:

            print("AUDIO ERROR:", e)

            return (
                "حدث خطأ أثناء إنشاء MP3.",
                500
            )

    return send_from_directory(
        DOWNLOAD_FOLDER,
        filename,
        as_attachment=True
    )


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
