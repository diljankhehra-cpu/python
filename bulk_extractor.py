import os
import requests
import re
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION ---
START_ID = int(os.environ.get("START_ID", 666))
END_ID = int(os.environ.get("END_ID", 2000))
OUTPUT_FILE = "playlist.m3u"
# ---------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

valid_channels = []

def parse_m3u8_info(m3u8_url, stream_id):
    try:
        # m3u8 file da content parho taan jo logo te naam mil sake
        res = requests.get(m3u8_url, headers=HEADERS, timeout=5)
        if res.status_code == 200 and "#EXTINF" in res.text:
            content = res.text
            
            # 1. Logo labhan lyi Regex (tvg-logo="...")
            logo_match = re.search(r'tvg-logo="([^"]+)"', content)
            logo = logo_match.group(1) if logo_match else ""
            
            # 2. Channel Name labhan lyi Regex
            # M3u8 ch aam tor te group-title ton baad ya line de aakhir ch naam hunda
            name_match = re.search(r',([^\n\r]+)', content)
            channel_name = name_match.group(1).strip() if name_match else f"Channel {stream_id}"
            
            # Agar name ch dubara m3u8 info hove taan clean karo
            if "#EXTINF" in channel_name:
                channel_name = f"Channel {stream_id}"

            print(f"[EXTRACTED] ID {stream_id} -> {channel_name}")
            return {"id": stream_id, "name": channel_name, "logo": logo, "url": m3u8_url}
    except Exception:
        pass
    
    # Je m3u8 parhan ch dikkat aave taan default info naal save karo
    return {"id": stream_id, "name": f"Channel {stream_id}", "logo": "", "url": m3u8_url}

def process_id(stream_id):
    url = f"https://mini.allinonereborn.fun/tata.php?id={stream_id}"
    try:
        response = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=5, stream=True)
        real_url = response.url
        response.close()
        
        if "tata.php" in real_url or response.status_code != 200:
            return 

        print(f"[FOUND] ID {stream_id} -> Redirected")
        
        # Asli m3u8 de andar ton logo te naam kaddho
        channel_info = parse_m3u8_info(real_url, stream_id)
        valid_channels.append(channel_info)
            
    except Exception:
        pass

if __name__ == "__main__":
    print(f"Starting auto M3U generation from ID {START_ID} to {END_ID}...")
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(process_id, range(START_ID, END_ID + 1))
        
    # --- M3U FILE GENERATION ---
    if valid_channels:
        # IDs de hisab naal line wise sort karo
        valid_channels.sort(key=lambda x: x["id"])
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for ch in valid_channels:
                # M3U format vich logo te naam likhna
                f.write(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-logo="{ch["logo"]}",{ch["name"]}\n')
                f.write(f'{ch["url"]}\n')
                
        print(f"Sira! {OUTPUT_FILE} file bann gayi hai total {len(valid_channels)} channels naal.")
    else:
        print("Koi valid stream ni mili.")
