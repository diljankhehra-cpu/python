import os
import requests
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor

START_ID = int(os.environ.get("START_ID", 666))
END_ID = int(os.environ.get("END_ID", 700))
OUTPUT_FILE = "channels.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

import easyocr
reader = easyocr.Reader(['en']) 

def clean_ocr_text(text_list, stream_id):
    """Kachra text saaf karan te asli channel name labhan lyi filter"""
    full_text = " ".join(text_list).strip()
    
    # 1. Faltu common garbage patterns te ad text uddao
    full_text = re.sub(r'\b(Find Your|PM|AM|Course|Year|Diploma|Tv|Journalism|Filmmaking|Acting|Weekend|Workshop|Headline|News 50|Tue|June|Sory|Download|Http|Https|Web)\b.*', '', full_text, flags=re.IGNORECASE)
    
    # 2. Sirf Numbers, special symbols (@, #, $, %, etc.) te tute-futte akhar saaf karo
    full_text = re.sub(r'[^a-zA-Z0-9\s:|-]', '', full_text)
    
    # Lines nu saaf karke single spaces bnao
    clean_name = " ".join(full_text.split()).strip()
    
    # 3. Agar naam bhot lamba hove (yaani ad text hai) ya khali hove, taan simple ID rakh do
    if not clean_name or len(clean_name) < 3 or len(clean_name) > 30:
        clean_name = f"Channel {stream_id}"
        
    return clean_name.upper()

def process_id(stream_id):
    base_url = f"https://mini.allinonereborn.fun/tata.php?id={stream_id}"
    temp_img = f"temp_{stream_id}.jpg"
    
    try:
        response = requests.get(base_url, headers=HEADERS, allow_redirects=True, timeout=5, stream=True)
        real_url = response.url
        response.close()
        
        if "tata.php" in real_url or response.status_code != 200:
            return 
            
        command = [
            'ffmpeg', '-y', '-timeout', '4000000',
            '-i', real_url, '-ss', '00:00:01', '-vframes', '1', temp_img
        ]
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12)
        
        if result.returncode == 0 and os.path.exists(temp_img):
            text_results = reader.readtext(temp_img, detail=0)
            
            # Kachra filter karke simple naam kadho
            channel_name = clean_ocr_text(text_results, stream_id)
            
            print(f"[CLEANED] ID {stream_id} -> {channel_name}")
            
            # --- STRICT SIMPLE FORMAT ---
            # Pehli line: Channel Name, Agli line: Link
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"{channel_name}\n{base_url}\n")
                
            os.remove(temp_img)
            
    except Exception:
        if os.path.exists(temp_img):
            os.remove(temp_img)

if __name__ == "__main__":
    print(f"Clean Scanning {START_ID} to {END_ID}...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(process_id, range(START_ID, END_ID + 1))
    print("Batch Complete!")
