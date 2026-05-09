from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
import time

def main():
    # 1. Thiết lập Chrome Options để chạy trên môi trường Server (GitHub Actions)
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Chạy ẩn danh
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    base_url = "https://sv2.hoiquan3.live"
    user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Mobile Safari/537.36"

    try:
        print("Đang mở trang web...")
        driver.get(f"{base_url}/trang-chu")
        
        # Đợi 10 giây để JavaScript load hết nội dung và link stream
        time.sleep(10)
        
        # Lấy toàn bộ mã nguồn sau khi đã thực thi JS
        page_source = driver.page_source
        
        # Tìm tất cả link m3u8
        m3u8_links = re.findall(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', page_source)
        
        playlist = "#EXTM3U\n"
        seen_streams = set()
        count = 0

        for stream in m3u8_links:
            stream = stream.replace('\\', '')
            if stream not in seen_streams:
                # Tạo title giả lập theo mẫu bạn yêu cầu
                playlist += f'#EXTINF:0 group-title="Hội quán" tvg-logo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTEFZhuqXE1ckKN_nKQg-3kz1LTeCN3GV-8kA&s",Trận đấu {count+1}\n'
                playlist += f'#EXTVLCOPT:http-user-agent={user_agent}\n'
                playlist += f'#EXTVLCOPT:http-referrer={base_url}/\n'
                playlist += f'{stream}\n'
                
                seen_streams.add(stream)
                count += 1

        if count > 0:
            with open("playlist.m3u", "w", encoding="utf-8") as f:
                f.write(playlist)
            print(f"Thành công: Đã lấy được {count} link bằng Selenium!")
        else:
            print("Thất bại: Selenium cũng không tìm thấy link m3u8 nào.")

    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
