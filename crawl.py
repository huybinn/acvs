import requests
from bs4 import BeautifulSoup
import re

def get_m3u8(url, headers):
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # Tìm link m3u8 trong mã nguồn
        match = re.search(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', res.text)
        if match:
            return match.group(1).replace('\\', '')
    except:
        pass
    return None

def main():
    base_url = "https://sv2.hoiquan3.live"
    target_url = f"{base_url}/trang-chu"
    user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36"
    headers = {"User-Agent": user_agent, "Referer": base_url + "/"}

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        playlist = "#EXTM3U\n"
        count = 0
        seen = set()

        for item in links:
            href = item['href']
            if "/video/" in href or "post" in href:
                full_link = href if href.startswith('http') else base_url + href
                if full_link not in seen:
                    m3u8_link = get_m3u8(full_link, headers)
                    if m3u8_link:
                        title = item.get('title') or item.text.strip() or f"Video {count+1}"
                        playlist += f'#EXTINF:-1 group-title="HoiQuan3",{title}\n'
                        playlist += f'#EXTVLCOPT:http-user-agent={user_agent}\n'
                        playlist += f'#EXTVLCOPT:http-referrer={base_url}/\n'
                        playlist += f'{m3u8_link}\n'
                        seen.add(full_link)
                        count += 1

        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write(playlist)
        print(f"Done! Found {count} links.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
