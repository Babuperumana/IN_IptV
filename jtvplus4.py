import json
import requests
from urllib.parse import urlparse

# URL of the JSON file
JSON_URL = "https://raw.githubusercontent.com/yashiscool123/TV-/refs/heads/main/jtv.json"

def fetch_json(url):
    
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def generate_m3u(channels):
    
    lines = ["#EXTM3U"]

    for ch in channels:
        # Required fields
        channel_id = ch.get("id", "")
        name = ch.get("name", "Unknown")
        key_id = ch.get("key_id", "")
        key = ch.get("key", "")
        stream_url = ch.get("stream_url", "")
        cookie = ch.get("cookie", "")

        # Build license key: key_id:key
        license_key = f"{key_id}:{key}" if key_id and key else ""

        # Construct tvg-logo (using a default pattern if not provided)
        # The example uses: https://jiotv.catchup.cdn.jio.com/dare_images/images/{name}.png
        # We'll generate a similar URL, but you can adjust if the JSON has a logo field.
        logo_name = name.replace(" ", "")
        tvg_logo = f"https://jiotv.catchup.cdn.jio.com/dare_images/images/{logo_name}.png"

        # Group title - default to "English" or derive from name
        group_title = "English"  # You can customize this logic

        # EXTINF line
        extinf = f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{name}" tvg-logo="{tvg_logo}" group-title="{group_title}",{name}'
        lines.append(extinf)

        # KODIPROP lines for inputstream adaptive
        lines.append("#KODIPROP:inputstream=inputstream.adaptive")
        lines.append("#KODIPROP:inputstream.adaptive.manifest_type=mpd")
        lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
        if license_key:
            lines.append(f"#KODIPROP:inputstream.adaptive.license_key={license_key}")

        # EXTVLCOPT and EXTHTTP for cookie
        # The example uses a fixed user-agent, but you can make it dynamic.
        lines.append("#EXTVLCOPT:http-user-agent=Sayan10")
        if cookie:
            # The EXTHTTP line should contain the cookie in JSON format
            # Example: #EXTHTTP:{"cookie": "..."}
            lines.append(f'#EXTHTTP:{{"cookie": "{cookie}"}}')

        # Stream URL
        lines.append(stream_url)

        # Blank line between entries (optional but improves readability)
        lines.append("")

    return "\n".join(lines)

def main():
    try:
        data = fetch_json(JSON_URL)
        # The JSON appears to be a list of channel objects
        if isinstance(data, list):
            channels = data
        else:
            # If it's a dict with a key containing the list, adjust accordingly
            # For now, assume it's a list
            print("Unexpected JSON format: root is not a list.")
            return

        m3u_content = generate_m3u(channels)

        # Write to a file
        output_file = "jtvplus4.m3u"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(m3u_content)

        print(f"M3U playlist generated successfully: {output_file}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
