import os
import requests
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

START_ID = int(os.environ.get("START_ID", 666))
END_ID = int(os.environ.get("END_ID", 750))
OUTPUT_FILE = "channels.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

import easyocr
# EasyOCR English model load karo
reader = easyocr.Reader(['en']) 

def clean_extracted_text(text_list, stream_id):
    """Bina static names de, extracted text nu pure dynamic filter karna"""
    valid_words = []
    
    for word in text_list:
        word = word.upper().strip()
        
        # 1. Chote tute akhar (len < 3) uddao
        if len(word) < 3:
            continue
            
        # 2. Sirf clean numbers te alphabets rkho (symbols saaf)
        clean_word = re.sub(r'[^A-Z0-9\s]', '', word).strip()
        
        # 3. Default text ya stream ID filter karo
        if clean_word.isdigit() or "CHANNEL" in clean_word or str(stream_id) in clean_word:
            continue
            
        # 4. Faltu live stream info filter out karo
        if any(tag in clean_word for tag in ["LIVE", "NOW", "FLAT", "LINE", "PLUS", "JUN", "TUE", "AM", "PM"]):
            continue
            
        if clean_word and not clean_word.isdigit():
            valid_words.append(clean_word)
            
    return " ".join(valid_words).strip()

def process_id(stream_id):
    base_url = f"https://mini.allinonereborn.fun/tata.php?id={stream_id}"
    temp_img = f"temp_{stream_id}.jpg"
    crop_left = f"crop_left_{stream_id}.jpg"
    crop_right = f"crop_right_{stream_id}.jpg"
    
    try:
        response = requests.get(base_url, headers=HEADERS, allow_redirects=True, timeout=5, stream=True)
        real_url = response.url
        response.close()
        
        if "tata.php" in real_url or response.status_code != 200:
            return 
            
        # 1. FFmpeg naal 2nd second te snapshot chkko
        command = [
            'ffmpeg', '-y', '-timeout', '4000000',
            '-i', real_url, '-ss', '00:00:02', '-vframes', '1', temp_img
        ]
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=14)
        
        if result.returncode == 0 and os.path.exists(temp_img):
            img = Image.open(temp_img)
            width, height = img.size
            
            # --- DYNAMIC CORNER CROPPING ---
            # Top-Left Corner Box (Top 20% height, Left 30% width)
            box_left = (0, 0, int(width * 0.30), int(height * 0.20))
            img.crop(box_left).save(crop_left)
            
            # Top-Right Corner Box (Top 20% height, Right 30% width)
            box_right = (int(width * 0.70), 0, width, int(height * 0.20))
            img.crop(box_right).save(crop_right)
            
            # 2. Dona corners ton text read karo
            text_left = reader.readtext(crop_left, detail=0)
            text_right = reader.readtext(crop_right, detail=0)
            
            # 3. Clean karo text nu
            clean_left = clean_extracted_text(text_left, stream_id)
            clean_right = clean_extracted_text(text_right, stream_id)
            
            # 4. Faisla karo ke channel name kehda rakhna hai
            if clean_left and clean_right:
                channel_name = f"{clean_left} {clean_right}"
            elif clean_left:
                channel_name = clean_left
            elif clean_right:
                channel_name = clean_right
            else:
                channel_name = f"CHANNEL {stream_id}"
                
            # Final validation (Je poora lamba kachra text hove taan standard fallback)
            if len(channel_name) > 30:
                channel_name = f"CHANNEL {stream_id}"
                
            print(f"[CORNER SUCCESS] ID {stream_id} -> {channel_name}")
            
            # STRICT SIMPLE 2-LINE FORMAT SAVE
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"{channel_name}\n{base_url}\n")
                
            # Faltu temp images saaf karo
            for f_path in [temp_img, crop_left, crop_right]:
                if os.path.exists(f_path): os.remove(f_path)
            
    except Exception:
        for f_path in [temp_img, crop_left, crop_right]:
            if os.path.exists(f_path): os.remove(f_path)

if __name__ == "__main__":
    print(f"Scanning Corners (Top-Left & Top-Right) from {START_ID} to {END_ID}...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_id, range(START_ID, END_ID + 1))
    print("Batch Complete!")
