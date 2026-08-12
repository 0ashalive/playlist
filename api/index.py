from http.server import BaseHTTPRequestHandler
import json
import urllib.request

JSON_URL = "https://jtvxweb.pages.dev/den-ww.json"


def parse_drm_key(drm_val):
    if not drm_val:
        return None

    # Handle Python dictionary format
    if isinstance(drm_val, dict):
        for k, v in drm_val.items():
            return f"{k}:{v}"

    # Handle string format (e.g., stringified JSON or pre-formatted key)
    if isinstance(drm_val, str):
        cleaned = drm_val.strip()
        if cleaned.lower() == "none" or not cleaned:
            return None

        # Check if string is serialized JSON dictionary
        if cleaned.startswith("{") and cleaned.endswith("}"):
            try:
                parsed_json = json.loads(cleaned)
                if isinstance(parsed_json, dict):
                    for k, v in parsed_json.items():
                        return f"{k}:{v}"
            except Exception:
                pass

        return cleaned

    return None


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            req = urllib.request.Request(
                JSON_URL, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            m3u_lines = ["#EXTM3U\n"]
            channels = (
                data
                if isinstance(data, list)
                else data.get("channels", data.get("result", [data]))
            )

            for ch in channels:
                name = ch.get("name") or ch.get("title") or "Unknown Channel"
                channel_id = (
                    ch.get("channel_id") or ch.get("id") or ch.get("tvg_id") or ""
                )
                category = (
                    ch.get("category")
                    or ch.get("group")
                    or ch.get("group_title")
                    or ""
                )
                logo = ch.get("logo") or ch.get("tvg_logo") or ch.get("icon") or ""

                raw_drm = (
                    ch.get("drm")
                    or ch.get("license_key")
                    or ch.get("key")
                    or ch.get("clearkey")
                )
                drm_key = parse_drm_key(raw_drm)

                user_agent = (
                    ch.get("userAgent")
                    or ch.get("user_agent")
                    or ch.get("agent")
                    or ""
                )
                token = ch.get("token") or ch.get("cookie") or ""
                mpd_link = (
                    ch.get("mpd")
                    or ch.get("link")
                    or ch.get("url")
                    or ch.get("mpd_url")
                    or ""
                )

                m3u_lines.append(
                    f'#EXTINF:-1 tvg-id="{channel_id}" group-title="{category}" tvg-logo="{logo}",{name}'
                )

                if drm_key:
                    m3u_lines.append(
                        "#KODIPROP:inputstream.adaptive.license_type=clearkey"
                    )
                    m3u_lines.append(
                        f"#KODIPROP:inputstream.adaptive.license_key={drm_key}"
                    )

                if user_agent:
                    m3u_lines.append(f"#EXTVLCOPT:http-user-agent={user_agent}")

                if token:
                    m3u_lines.append(f'#EXTHTTP:{{ "cookie":"{token}" }}')

                m3u_lines.append(f"{mpd_link}\n")

            output = "\n".join(m3u_lines).strip()

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header(
                "Cache-Control", "no-cache, no-store, must-revalidate"
            )
            self.end_headers()
            self.wfile.write(output.encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            err_msg = f"#EXTM3U\n#ERROR: {str(e)}"
            self.wfile.write(err_msg.encode("utf-8"))
            
