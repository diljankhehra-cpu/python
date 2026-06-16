import os
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

START_ID = int(os.environ.get("START_ID", 1000))
END_ID = int(os.environ.get("END_ID", 1050)) # Chote batch ch chalao taan jo safe rahe
OUTPUT_FILE = "channels.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

import easyocr
reader = easyocr.Reader(['en']) 

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
            
        # 1. FFMPEG naal sirf 1 stable frame kadho
        command = [
            'ffmpeg', '-y', '-timeout', '4000000',
            '-i', real_url, '-ss', '00:00:02', '-vframes', '1', temp_img
        ]
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        
        if result.returncode == 0 and os.path.exists(temp_img):
            # 2. Image open karke sirf Top Area (Logo space) crop karo
            img = Image.open(temp_img)
            width, height = img.size
            
            # Sirf screen da top 20% hissa chkko (jithe channel logo hunde ne)
            # Baaki thalleya kachra, ads, movies name automatic udd jange
            box = (0, 0, width, int(height * 0.22))
            cropped = img.crop(box)
            cropped.save(crop_img)
            
            # 3. Crop keeti photo te OCR chalao
            text_results = reader.readtext(crop_img, detail=0)
            channel_name = " ".join(text_results).strip().upper()
            
            if not channel_name or len(channel_name) < 3:
                channel_name = f"CHANNEL {stream_id}"
                
            print(f"[CROP OCR] ID {stream_id} -> {channel_name}")
            
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"{channel_name}\n{base_url}\n")
                
            # Safai karo files di
            if os.path.exists(temp_img): os.remove(temp_img)
            if os.path.exists(crop_img): os.remove(crop_img)
            
    except Exception:
        if os.path.exists(temp_img): os.remove(temp_img)
        if os.path.exists(crop_img): os.remove(crop_img)

if __name__ == "__main__":
    print(f"Scanning with Crop OCR from {START_ID} to {END_ID}...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_id, range(START_ID, END_ID + 1))
    print("Batch Complete!")
