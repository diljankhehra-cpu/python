import os
import requests
import re
from concurrent.futures import ThreadPoolExecutor

START_ID = int(os.environ.get("START_ID", 666))
END_ID = int(os.environ.get("END_ID", 1000)) # Hun tusi 500-1000 IDs da batch chala sakde ho kyonki eh bhot fast hai
OUTPUT_FILE = "channels.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def parse_accurate_name(m3u8_url, stream_id):
    """m3u8 file de andar vadke asli channel name te logo kadhan lyi"""
    try:
        # m3u8 file da content fetch karo
        response = requests.get(m3u8_url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            content = response.text
            
            # 1. Check karo je #EXTINF de andar group-title ya tvg-name likhya hove
            # Providers aam tor te aiven likhde ne: tvg-name="STAR SPORTS 1" ya group-title="SPORTS"
            name_match = re.search(r'tvg-name="([^"]+)"', content)
            if not name_match:
                name_match = re.search(r'group-title="([^"]+)"', content)
            
            if name_match:
                return name_match.group(1).strip().upper()
            
            # 2. Je ਉੱਪਰਲਾ ਕੁਝ ਨਾ ਮਿਲੇ, ਤਾਂ line ਦੇ ਆਖਿਰ ਵਾਲਾ ਸਾਫ ਨਾਮ ਚੱਕੋ (ਜੋ comma , ਤੋਂ ਬਾਅਦ ਹੁੰਦਾ ਹੈ)
            lines = content.split('\n')
            for line in lines:
                if "#EXTINF" in line and "," in line:
                    clean_name = line.split(",")[-1].strip()
                    if clean_name and not clean_name.startswith("#"):
                        return clean_name.upper()
                        
    except Exception:
        pass
    
    # Je m3u8 content chon v na miley, taan default standard name rakh do
    return f"CHANNEL {stream_id}"

def process_id(stream_id):
    base_url = f"https://mini.allinonereborn.fun/tata.php?id={stream_id}"
    
    try:
        # Sirf network redirect follow karna hai, zero video downloading!
        response = requests.get(base_url, headers=HEADERS, allow_redirects=True, timeout=5, stream=True)
        real_url = response.url
        response.close()
        
        if "tata.php" in real_url or response.status_code != 200:
            return 
            
        # Asli m3u8 de andar vad ke accurate naam kaddho
        channel_name = parse_accurate_name(real_url, stream_id)
        
        print(f"[PARSED SUCCESS] ID {stream_id} -> {channel_name}")
        
        # Tuhade ditte strict 2-line format vich save karna
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"{channel_name}\n{base_url}\n")
            
    except Exception:
        pass

if __name__ == "__main__":
    print(f"Metadata Scanning {START_ID} to {END_ID}...")
    # Network calls fast hundiyan ne, es lyi workers vadha ditte
    with ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(process_id, range(START_ID, END_ID + 1))
    print("Batch Complete!")
