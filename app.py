from flask import Flask, Response, request
import requests
import re

app = Flask(__name__)

# আসল m3u8 URL (এখানে আপনার লিংক দিন)
SOURCE_URL = "https://example.com/live/stream.m3u8"


@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Stream Proxy</title>
    </head>
    <body>
        <h2>Live Stream via Proxy</h2>
        <video width="640" height="360" controls autoplay>
            <source src="/playlist.m3u8" type="application/vnd.apple.mpegurl">
            Your browser does not support the video tag.
        </video>
    </body>
    </html>
    """


@app.route("/playlist.m3u8")
def playlist():
    # আসল m3u8 কন্টেন্ট নিয়ে আসা
    r = requests.get(SOURCE_URL)
    content = r.text

    # ts সেগমেন্টকে প্রোক্সি লিংকে কনভার্ট করা
    def replace_segment(match):
        segment_url = match.group(0).strip()
        return f"/segment?url={segment_url}"

    new_content = re.sub(r".*\.ts", replace_segment, content)

    return Response(new_content, content_type="application/vnd.apple.mpegurl")


@app.route("/segment")
def segment():
    segment_url = request.args.get("url")

    # যদি রিলেটিভ পাথ হয় → SOURCE_URL এর বেস যুক্ত করা
    if not segment_url.startswith("http"):
        base_url = SOURCE_URL.rsplit("/", 1)[0]
        segment_url = f"{base_url}/{segment_url}"

    r = requests.get(segment_url, stream=True)
    return Response(r.iter_content(chunk_size=1024),
                    content_type="video/MP2T")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
