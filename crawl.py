import requests
from bs4 import BeautifulSoup
import re

def get_m3u8(url, headers):
    try:
        # Tăng timeout lên một chút để trang kịp load
        res = requests.get(url, headers=headers, timeout=15)
        # Regex này sẽ tìm mọi chuỗi kết thúc bằng .m3u8 bên trong code
        match = re.search(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', res.text)
        if match:
            link = match.group(1).replace('\\', '')
            return link
    except:
        pass
    return None

def main():
    base_url = "https://sv2.hoiquan3.live"
    target_url = f"{base_url}/trang-chu"
    
    # Dùng User-Agent mobile để web trả về giao diện nhẹ, dễ crawl hơn
    user_agent = "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36"
    headers = {
        "User-Agent": user_agent,
        "Referer": base_url + "/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    try:
        session = requests.Session()
        response = session.get(target_url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm tất cả thẻ <a> trên toàn bộ trang không phân biệt class
        all_links = soup.find_all('a', href=True)
        
        playlist = "#EXTM3U\n"
        count = 0
        seen_urls = set()

        print(f"Tổng số link tìm thấy trên trang chủ: {len(all_links)}")

        for item in all_links:
            href = item['href']
            
            # Chỉ bỏ qua các link rác (facebook, zalo, telegram, v.v.)
            if any(x in href for x in ['facebook', 'zalo', 'tele', 'javascript', '#']):
                continue
                
            full_link = href if href.startswith('http') else base_url + href
            
            # Nếu link là link nội bộ (video hoặc post), tiến hành đào sâu
            if base_url in full_link and full_link not in seen_urls:
                m3u8_link = get_m3u8(full_link, headers)
                
                if m3u8_link:
                    title = item.text.strip() or item.get('title') or f"Video {count+1}"
                    # Làm sạch title (bỏ xuống dòng, khoảng trắng thừa)
                    title = " ".join(title.split())
                    
                    playlist += f'#EXTINF:-1 group-title="HoiQuan3",{title}\n'
                    playlist += f'#EXTVLCOPT:http-user-agent={user_agent}\n'
                    playlist += f'#EXTVLCOPT:http-referrer={base_url}/\n'
                    playlist += f'{m3u8_link}\n'
                    
                    seen_urls.add(full_link)
                    count += 1
                    print(f"Đã lấy: {title}")

        if count > 0:
            with open("playlist.m3u", "w", encoding="utf-8") as f:
                f.write(playlist)
            print(f"Thành công! Đã lưu {count} mục vào playlist.m3u")
        else:
            print("Vẫn không tìm thấy video. Có thể trang web dùng JavaScript để ẩn link.")

    except Exception as e:
        print(f"Lỗi chính: {e}")

if __name__ == "__main__":
    main()
