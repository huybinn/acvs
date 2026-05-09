import requests
from bs4 import BeautifulSoup
import re

def get_m3u8(url, headers):
    try:
        # Thêm timeout và allow_redirects để tránh bị treo
        res = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        # Tìm link m3u8 với Regex chính xác hơn
        match = re.search(r'["\'](https?://[^\s\'"]+\.m3u8[^\s\'"]*)["\']', res.text)
        if not match:
            match = re.search(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', res.text)
            
        if match:
            link = match.group(1).replace('\\', '')
            return link
    except Exception as e:
        print(f"Lỗi khi vào trang chi tiết {url}: {e}")
    return None

def main():
    base_url = "https://sv2.hoiquan3.live"
    target_url = f"{base_url}/trang-chu"
    
    # Header mô phỏng cực giống trình duyệt thật
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    headers = {
        "User-Agent": user_agent,
        "Referer": base_url + "/",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        session = requests.Session() # Dùng Session để giữ kết nối
        response = session.get(target_url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Lấy tất cả các link trên trang
        links = soup.find_all('a', href=True)
        
        playlist = "#EXTM3U\n"
        count = 0
        seen = set()

        for item in links:
            href = item['href']
            # Lọc linh hoạt hơn các link chứa video
            if any(x in href for x in ["/video/", "/post/", "/watch/"]):
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
                        print(f"Tìm thấy: {title}")

        # Chỉ ghi file nếu có dữ liệu
        if count > 0:
            with open("playlist.m3u", "w", encoding="utf-8") as f:
                f.write(playlist)
            print(f"Thành công! Đã lưu {count} kênh.")
        else:
            print("Không tìm thấy link nào, kiểm tra lại cấu trúc web!")

    except Exception as e:
        print(f"Lỗi chính: {e}")

if __name__ == "__main__":
    main()
