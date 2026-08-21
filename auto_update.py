import os
import json
import re
import urllib.request
from urllib.error import URLError, HTTPError
import shutil

# Priority list of M3U files to check
PLAYLISTS = [
    'jtv.m3u',
    'jtv2.m3u',
    'jtv3.m3u',
    'jtv4.m3u',
    'jtv5.m3u',
    'jtvplus.m3u',
    'jtvplus2.m3u',
    'jtvplus3.m3u'
]

def extract_channel_data(file_path):
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    stream_url = None
    token = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('#EXTHTTP:'):
            try:
                json_str = line[9:]
                data = json.loads(json_str)
                if 'cookie' in data:
                    match = re.search(r'__hdnea__=([^;]+)', data['cookie'])
                    if match:
                        token = match.group(1)
            except Exception as e:
                pass
                
        elif not line.startswith('#'):
            # This is a stream URL
            stream_url = line
            # If the token is already in the URL
            match = re.search(r'__hdnea__=([^&]+)', stream_url)
            if match:
                token = match.group(1)
                
            # Once we find the first stream URL, we can break and test it!
            if stream_url and token:
                break
                
    if stream_url and token:
        # Construct the final test URL
        if '__hdnea__' not in stream_url:
            separator = '&' if '?' in stream_url else '?'
            test_url = f"{stream_url}{separator}__hdnea__={token}"
        else:
            test_url = stream_url
        return test_url
        
    return None

def test_url(url):
    try:
        print(f"Testing URL: {url[:100]}...")
        # Add a standard user agent just in case
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=10)
        return response.getcode() == 200
    except HTTPError as e:
        print(f"HTTP Error: {e.code}")
        return False
    except URLError as e:
        print(f"URL Error: {e.reason}")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    working_playlist = None
    
    for playlist in PLAYLISTS:
        print(f"Checking playlist: {playlist}")
        test_url_path = extract_channel_data(playlist)
        
        if not test_url_path:
            print(f"  -> Could not extract a valid stream URL and token from {playlist}")
            continue
            
        is_working = test_url(test_url_path)
        
        if is_working:
            print(f"  -> SUCCESS! Playlist '{playlist}' is working.")
            working_playlist = playlist
            break
        else:
            print(f"  -> FAILED! Playlist '{playlist}' is dead or expired.")
            
    if working_playlist:
        print(f"\nCopying {working_playlist} to final.m3u...")
        shutil.copyfile(working_playlist, 'final.m3u')
        print("Done.")
    else:
        print("\nCRITICAL: No working playlists found in the entire list!")

if __name__ == "__main__":
    main()
