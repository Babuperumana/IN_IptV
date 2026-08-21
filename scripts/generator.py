import requests
import json
import os

# You can change this to any JSON endpoint that provides channel metadata
JSON_URL = os.getenv("JSON_URL", "https://m3u-86e.pages.dev/jtv-mb.json")
OUTPUT_FILE = "playlist.m3u"
USER_AGENT = "IN_IptV/1.0"

def generate_playlist():
    print(f"Fetching channel data from {JSON_URL}...")
    try:
        response = requests.get(JSON_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Depending on the JSON structure, it could be a list or dict. We assume a list based on standard formats.
        if isinstance(data, dict) and "channels" in data:
            channels = data["channels"]
        elif isinstance(data, list):
            channels = data
        else:
            print("Unknown JSON format.")
            return

        print(f"Found {len(channels)} channels. Generating M3U...")
        
        m3u_lines = ["#EXTM3U"]
        
        for ch in channels:
            # Extract standard fields (with fallbacks)
            name = ch.get("name", "Unknown Channel")
            ch_id = ch.get("id", "")
            logo = ch.get("logo", "")
            group = ch.get("group", "General")
            
            # Extract stream and DRM details
            stream_url = ch.get("mpd_url", ch.get("stream_url", ""))
            license_url = ch.get("license_url", "")
            
            if not stream_url:
                continue
                
            # EXTINF tag
            m3u_lines.append(f'#EXTINF:-1 tvg-id="{ch_id}" tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}')
            
            # DRM configuration for Kodi/Inputstream Adaptive
            if "dash" in str(ch.get("type", "")).lower() or ".mpd" in stream_url.lower():
                m3u_lines.append("#KODIPROP:inputstream.adaptive.manifest_type=mpd")
                
            if license_url or (ch.get("key_id") and ch.get("key")):
                m3u_lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
                
                # Check if it's a URL or a KeyID:Key format
                if license_url:
                    m3u_lines.append(f"#KODIPROP:inputstream.adaptive.license_key={license_url}")
                else:
                    m3u_lines.append(f"#KODIPROP:inputstream.adaptive.license_key={ch.get('key_id')}:{ch.get('key')}")
            
            # Add Custom User-Agent if available
            if ch.get("user_agent"):
                m3u_lines.append(f"#EXTVLCOPT:http-user-agent={ch.get('user_agent')}")

            # Add Custom Headers if available
            headers = ch.get("headers", {})
            if headers:
                if isinstance(headers, dict):
                    m3u_lines.append(f"#EXTHTTP:{json.dumps(headers)}")
                else: # It might be a string already
                    m3u_lines.append(f"#EXTHTTP:{headers}")
            elif ch.get("cookie"):
                default_headers = {"cookie": ch.get("cookie"), "Origin": "https://www.jiotv.com/", "Referer": "https://www.jiotv.com/"}
                m3u_lines.append(f"#EXTHTTP:{json.dumps(default_headers)}")

            # Stream URL
            m3u_lines.append(stream_url)
            m3u_lines.append("") # Blank line
            
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(m3u_lines))
            
        print(f"Playlist successfully saved to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Error generating playlist: {e}")

if __name__ == "__main__":
    generate_playlist()
