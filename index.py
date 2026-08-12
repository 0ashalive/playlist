from flask import Flask, Response
import requests

# MUST be exposed at top-level
app = Flask(__name__)

JSON_URL = "https://jtvxweb.pages.dev/den-ww.json"


def build_m3u(data):
    channels = (
        data
        if isinstance(data, list)
        else data.get("channels", data.get("result", [data]))
    )
    m3u_lines = ["#EXTM3U\n"]

    for ch in channels:
        name = ch.get("name") or ch.get("title") or "Unknown Channel"
        channel_id = ch.get("channel_id") or ch.get("id") or ch.get("tvg_id") or ""
        category = (
            ch.get("category") or ch.get("group") or ch.get("group_title") or ""
        )
        logo = ch.get("logo") or ch.get("tvg_logo") or ch.get("icon") or ""

        drm_key = (
            ch.get("drm")
            or ch.get("license_key")
            or ch.get("key")
            or ch.get("clearkey")
            or ""
        )
        user_agent = (
            ch.get("userAgent") or ch.get("user_agent") or ch.get("agent") or ""
        )
        token = ch.get("token") or ch.get("cookie") or ""
        mpd_link = (
            ch.get("mpd") or ch.get("link") or ch.get("url") or ch.get("mpd_url") or ""
        )

        m3u_lines.append(
            f'#EXTINF:-1 tvg-id="{channel_id}" group-title="{category}" tvg-logo="{logo}",{name}'
        )
        m3u_lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")

        if drm_key and str(drm_key).lower() != "none":
            m3u_lines.append(f"#KODIPROP:inputstream.adaptive.license_key={drm_key}")

        if user_agent:
            m3u_lines.append(f"#EXTVLCOPT:http-user-agent={user_agent}")

        if token:
            m3u_lines.append(f'#EXTHTTP:{{ "cookie":"{token}" }}')

        m3u_lines.append(f"{mpd_link}\n")

    return "\n".join(m3u_lines)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def get_playlist(path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    try:
        res = requests.get(JSON_URL, headers=headers, timeout=12)
        res.raise_for_status()
        data = res.json()

        m3u_output = build_m3u(data)

        return Response(
            m3u_output.strip(),
            mimetype="text/plain; charset=utf-8",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "no-cache, no-store, must-revalidate",
            },
        )
    except Exception as e:
        error_msg = f"#EXTM3U\n#ERROR: Could not fetch JSON data ({str(e)})"
        return Response(
            error_msg,
            status=500,
            mimetype="text/plain; charset=utf-8",
            headers={"Access-Control-Allow-Origin": "*"},
        )
