from http.server import BaseHTTPRequestHandler
import json
import urllib.request

# Directly set the single fast JSON endpoint
TARGET_URL = "https://jtvxweb.pages.dev/den-ww.json"


def parse_drm_key(ch):
    """Parses DRM keys across both dict formats and keyId/key parameters."""
    key_id = ch.get("keyId") or ch.get("key_id") or ch.get("kid") or ""
    key = ch.get("key") or ch.get("k") or ch.get("license_key") or ""

    if key_id and key and isinstance(key, str) and isinstance(key_id, str):
        if key.startswith("{") and key.endswith("}"):
            try:
                parsed = json.loads(key)
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        return f"{k}:{v}"
            except Exception:
                pass
        return f"{key_id}:{key}"

    raw_drm = ch.get("drm") or ch.get("clearkey")
    if isinstance(raw_drm, dict):
        for k, v in raw_drm.items():
            return f"{k}:{v}"

    if isinstance(raw_drm, str):
        cleaned = raw_drm.strip()
        if cleaned.lower() == "none" or not cleaned:
            return None
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
                TARGET_URL,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
                },
            )

            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))

            m3u_lines = ["#EXTM3U\n"]
            channels = (
                data
                if isinstance(data, list)
                else (
                    data.get("channels")
                    or data.get("result")
                    or data.get("data")
                    or [data]
                )
            )

            for ch in channels:
                if not isinstance(ch, dict):
                    continue

                name = ch.get("name") or ch.get("title") or "Unknown Channel"
                channel_id = (
                    ch.get("id") or ch.get("channel_id") or ch.get("tvg_id") or ""
                )
                category = (
                    ch.get("category")
                    or ch.get("group")
                    or ch.get("group_title")
                    or ""
                )
                logo = ch.get("logo") or ch.get("tvg_logo") or ch.get("icon") or ""
                mpd_link = (
                    ch.get("url")
                    or ch.get("mpd")
                    or ch.get("link")
                    or ch.get("mpd_url")
                    or ""
                )

                drm_key = parse_drm_key(ch)
                token = ch.get("token") or ch.get("cookie") or ""

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

                # Fixed User-Agent and Referrer tags
                m3u_lines.append(
                    "#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
                )
                m3u_lines.append(
                    "#EXTVLCOPT:http-referrer=https://jtvxweb.pages.dev/"
                )

                # Construct dynamic JSON header dict including the channel token
                exthttp_headers = {
                    "origin": "https://jtvxweb.pages.dev",
                    "referer": "https://jtvxweb.pages.dev/",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "cross-site",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
                    "cookie": token,
                }

                m3u_lines.append(f"#EXTHTTP:{json.dumps(exthttp_headers)}")
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
                    or ch.get("mpd")
                    or ch.get("link")
                    or ch.get("mpd_url")
                    or ""
                )

                drm_key = parse_drm_key(ch)
                user_agent = (
                    ch.get("userAgent")
                    or ch.get("user_agent")
                    or ch.get("agent")
                    or ""
                )
                token = ch.get("token") or ch.get("cookie") or ""

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
