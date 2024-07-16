import requests
import os

def download_m3u8_playlist(m3u8_url, output_file):
    response = requests.get(m3u8_url)
    playlist_content = response.text

    base_url = os.path.dirname(m3u8_url)
    segment_urls = []

    for line in playlist_content.splitlines():
        if line and not line.startswith("#"):
            segment_urls.append(os.path.join(base_url, line))
    
    with open(output_file, 'wb') as output:
        for segment_url in segment_urls:
            segment_response = requests.get(segment_url)
            output.write(segment_response.content)

# Example usage
m3u8_url = "https://example.com/path/to/playlist.m3u8"
output_file = "output_video.ts"
download_m3u8_playlist(m3u8_url, output_file)
