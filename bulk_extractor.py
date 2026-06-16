import os
import requests
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

START_ID = int(os.environ.get("START_ID", 1000))
END_ID = int(os.environ.get("END_ID", 1050))
OUTPUT_FILE = "channels.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Standard Channel List - Je ehna chon koi v akhar text ch dikhya, taan naam automatic clean ho javega
KNOWN_BRANDS = [
    "STAR", "SONY", "ZEE", "SUN", "NDTV", "VASANTH", "LIVING INDIA", "GOODTIMES", 
    "COLORS", "PTC", "MH1", "MOVIES", "NEWS", "SPORTS", "TEN", "DISCOVERY", 
    "ANIMAL PLANET", "TLC", "MTV", "BINDASS", "CARTOON", "NICK", "POGO"
]

import easyocr
reader = easyocr.Reader(['en']) 

def filter_smart_name(text_list, stream_id):
    full_text = " ".join(text_list).upper()
    
    # 1. Pehla check karo je koi janya-pachanya brand name match hunda hai
    for brand in KNOWN_BRANDS:
        if brand in full_text:
            # Je brand mil jave, taan text chon faltu symbols saaf karke 2-3 vaild words rkho
            clean_brand_text = re.sub(r'[^A-Z0-9\s]', '', full_text)
            words = clean_brand_text.split()
            # Brand de aale-duale de main words chkk lo (e.g., STAR MOVIES HD)
            idx = words.index(brand.split()[0])
            extracted = " ".join(words[idx:idx+4])
            return extracted
            
    # 2. Je koi brand na miley, taan tute-futte akhar saaf karo
    clean_text = re.sub(r'[^A-Z0-9\s]', '', full_text)
    words = [w for w in clean_text.split() if len(w) > 2 and not w.isdigit()]
    
    final_name = " ".join(words).strip()
    
    # 3. Je poora hi kachra hove, taan simple Channel ID rkho
    if not final_name or len(final_name) < 3 or len(final_name) > 25:
        return f"CHANNEL {stream_id}"
        
    return final_name

def process_id(stream_id):
    base_url = f"https://mini.allinonereborn.fun/tata.php?id={stream_id}"
    temp_img = f"temp_{stream_id}.jpg"
    crop_img = f"crop_{stream_id}.jpg"
    
    try:
        response = requests.get(base_url, headers=HEADERS, allow_redirects=True, timeout=5, stream=True)
        real_url = response.url
        response.close()
        
        if "tata.php" in real_url or response.status_code != 200:
            return 
            
        command = [
            'ffmpeg', '-y', '-timeout', '4000000',
            '-i', real_url, '-ss', '00:00:02', '-vframes', '1', temp_img
        ]
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=14)
        
        if result.returncode == 0 and os.path.exists(temp_img):
            img = Image.open(temp_img)
            width, height = img.size
            
            # Top 22% logo area crop
            box = (0, 0, width, int(height * 0.22))
            cropped = img.crop(box)
            cropped.save(crop_img)
            
            text_results = reader.readtext(crop_img, detail=0)
            
            # Smart filter lagao
            channel_name = filter_smart_name(text_results, stream_id)
            
            print(f"[SMART CLEAN] ID {stream_id} -> {channel_name}")
            
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"{channel_name}\n{base_url}\n")
                
            if os.path.exists(temp_img): os.remove(temp_img)
            if os.path.exists(crop_img): os.remove(crop_img)
            
    except Exception:
        if os.path.exists(temp_img): os.remove(temp_img)
        if os.path.exists(crop_img): os.remove(crop_img)

if __name__ == "__main__":
    print(f"Smart Scanning from {START_ID} to {END_ID}...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_id, range(START_ID, END_ID + 1))
    print("Batch Complete!")
