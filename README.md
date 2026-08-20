# IN_IptV

An automated IPTV playlist generator. 
This repository fetches the latest stream links and DRM keys for various channels and automatically builds a standard `.m3u` playlist every 30 minutes via GitHub Actions.

## How to Use
1. Copy the raw URL of the generated `playlist.m3u` file.
2. Paste it into any supported IPTV player (like Kodi, TiviMate, VLC, OTT Navigator).
3. The playlist will auto-update!

## Automation
The python script `scripts/generator.py` is executed via GitHub Actions to fetch JSON sources and format them into an M3U file containing:
- Stream URLs
- DRM ClearKey Keys
- HTTP Headers & User Agents
