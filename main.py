import json
import requests

JSON_URL = "https://jtvxweb.pages.dev/den-ww.json"

# Set a standard browser User-Agent header to prevent blocking
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def build_m3u_playlist(data):
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

        # DRM & Headers extraction
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

        # Output EXTINF header
        m3u_lines.append(
            f'#EXTINF:-1 tvg-id="{channel_id}" group-title="{category}" tvg-logo="{logo}",{name}'
        )
        m3u_lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")

        # Output ClearKey DRM if present
        if drm_key and drm_key.lower() != "none":
            m3u_lines.append(f"#KODIPROP:inputstream.adaptive.license_key={drm_key}")

        if user_agent:
            m3u_lines.append(f"#EXTVLCOPT:http-user-agent={user_agent}")

        if token:
            m3u_lines.append(f'#EXTHTTP:{{ "cookie":"{token}" }}')

        # Output MPD Link
        m3u_lines.append(f"{mpd_link}\n")

    return "\n".join(m3u_lines)


def main():
    try:
        # Direct GET request without proxy
        response = requests.get(JSON_URL, headers=headers, timeout=15)
        response.raise_for_status()

        json_data = response.json()
        m3u_playlist = build_m3u_playlist(json_data)

        # 1. Print plain text output directly to terminal/console
        print(m3u_playlist)

        # 2. Save directly to a .m3u file
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write(m3u_playlist)

        # print("\n[+] Playlist successfully saved to playlist.m3u")

    except requests.exceptions.RequestException as e:
        print(f"#EXTM3U\n#ERROR: Failed to fetch JSON playlist: {e}")


if __name__ == "__main__":
    main()
  
