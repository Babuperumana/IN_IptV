import urllib3
import urllib
import json
import time
playlist = ["#EXTM3U"]

resp = urllib3.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/get/token?tenant_code=yuppfast&box_id=3b6f5839-0b53-aa06-7a80-023047a6357c&product=yuppfast&device_id=5&display_lang_code=ENG&device_sub_type=Chrome,145.0.0.0,Windows&client_app_version=1&timezone=Asia/Calcutta",
    headers={
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "Referer": "https://www.yupptv.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    }
)

jsonresp = resp.json()

sessionid = jsonresp['response']['sessionId']

resp = urllib3.request(
    "GET",
    "https://yuppfast-api.revlet.net/service/api/v1/tvguide/channels?filter=genreCode:all;langCode:ENG,HIN,TAM,MAR,BEN,TEL,KAN,BHO,GUA,PUN,ASS,URD",
    headers={
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
        "Tenant-Code": "yuppfast",
        "Origin": "https://www.yupptv.com",
        "Referer": "https://www.yupptv.com/",
        "Session-Id": sessionid,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
    }
)

jsonresp = resp.json()

for i in jsonresp['response']['data']:
    stringdata = json.dumps(i, indent=4)
    channel_data = json.loads(stringdata)
    path = channel_data['target']['path']
    epg = channel_data['id']
    name = channel_data['display']['title']
    logo = channel_data['display']['imageUrl'].replace("common,", "https://d229kpbsb5jevy.cloudfront.net/yuppfast/content/common/")
    playlist.append(f'#EXTINF:-1 tvg-id="{epg}" tvg-chno="{epg}" tvg-name="{name}" tvg-logo="{logo}",{epg} {name}')
    encodedpath = urllib.parse.quote_plus(path)
    resp = urllib3.request(
        "GET",
        f"https://yuppfast-api.revlet.net/service/api/v1/page/stream?path={encodedpath}",
        headers={
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Box-Id": "3b6f5839-0b53-aa06-7a80-023047a6357c",
            "Tenant-Code": "yuppfast",
            "Origin": "https://www.yupptv.com",
            "Referer": "https://www.yupptv.com/",
            "Session-Id": sessionid,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        }
    )
    stream = resp.json()
    if stream['status'] == True:
        for j in stream['response']['streams']:
            streamlinks = []
            streamlinks.append(j['url'])
        playlist.append(streamlinks[0])
    else:
        playlist.append('')

with open('./yupptvfast.m3u', 'w', newline='') as f:
    for lines in playlist:
        f.write(f'{lines}\n')

f.close()
