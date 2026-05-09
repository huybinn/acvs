import requests
from bs4 import BeautifulSoup
import re

def get_direct_stream(url, headers):
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # Tìm link m3u8 từ các CDN phổ biến (edgemaxcdn, bpmedialive, etc.)
        match = re.search(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', res.text)
        if match:
            return match.group(1).replace('\\', '')
    except:
        pass
    return None

def main():
    base_url = "https://sv2.hoiquan3.live"
    target_url = f"{base_url}/trang-chu"
    
    # User-Agent chuẩn theo mẫu bạn gửi
    user_agent = "Mozilla AppleWebKit Chrome Safari"
    headers = {
        "User-Agent": user_agent,
        "Referer": "https://sv2.hoiquan3.live/"
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm tất cả các khối chứa trận đấu (thường là thẻ div hoặc a)
        items = soup.find_all(['a', 'div'], cursor=True) or soup.find_all('a', href=True)
        
        playlist = "#EXTM3U\n"
        count = 0
        seen_streams = set()

        for item in items:
            href = item.get('href') or item.get('data-link')
            if not href or "javascript" in href: continue
            
            full_link = href if href.startswith('http') else base_url + href
            
            # Chỉ lấy các link dẫn đến trang xem trực tiếp
            if any(x in full_link for x in ["/live/", "/xem-truc-tiep/", "/post/"]):
                stream_url = get_direct_stream(full_link, headers)
                
                if stream_url and stream_url not in seen_streams:
                    # Lấy tiêu đề và logo (nếu có)
                    title = item.text.strip() or "Trận đấu đang diễn ra"
                    logo = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTEFZhuqXE1ckKN_nKQg-3kz1LTeCN3GV-8kA&s"
                    
                    # Xây dựng nội dung theo đúng mẫu bạn yêu cầu
                    playlist += f'#EXTINF:0 group-title="Hội quán" tvg-logo="{logo}",{title}\n'
                    playlist += f'#EXTVLCOPT:http-user-agent={user_agent}\n'
                    playlist += f'#EXTVLCOPT:http-referrer=https://sv2.hoiquan3.live/\n'
                    playlist += f'{stream_url}\n'
                    
                    seen_streams.add(stream_url)
                    count += 1
                    print(f"Đã thêm: {title}")

        if count > 0:
            with open("playlist.m3u", "w", encoding="utf-8") as f:
                f.write(playlist)
            print(f"Thành công! Đã cập nhật {count} trận đấu.")
        else:
            # Trường hợp đặc biệt: Nếu không tìm thấy link qua thẻ a, quét toàn bộ trang chủ
            print("Đang thử quét sâu toàn trang...")
            direct_match = re.findall(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', response.text)
            if direct_match:
                # Xử lý tương tự nếu tìm thấy link m3u8 ngay tại trang chủ
                pass

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    main()
