import os
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION ---
START_ID = int(os.environ.get("START_ID", 666))
END_ID = int(os.environ.get("END_ID", 700)) # Default range
OUTPUT_FILE = "channels.txt"
# ---------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# EasyOCR initialize karo (eh automatic pehli vaar model download karega)
import easyocr
reader = easyocr.Reader(['en']) # English channels/logos lyi

def process_id(stream_id):
    # Tuhada ditta hoya asli bin-token wala link
    base_url = f"https://mini.allinonereborn.fun/tata.php?id={stream_id}"
    temp_img = f"temp_{stream_id}.jpg"
    
    try:
        # 1. Asli redirect url labho ffmpeg lyi
        response = requests.get(base_url, headers=HEADERS, allow_redirects=True, timeout=5, stream=True)
        real_url = response.url
        response.close()
        
        if "tata.php" in real_url or response.status_code != 200:
            return 
            
        # 2. FFMPEG naal choti photo extraction (sirf 1 frame)
        command = [
            'ffmpeg', '-y', '-timeout', '3000000',
            '-i', real_url, '-ss', '00:00:01', '-vframes', '1', temp_img
        ]
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12)
        
        if result.returncode == 0 and os.path.exists(temp_img):
            # 3. OCR rahin photo chon text read karna
            text_results = reader.readtext(temp_img, detail=0)
            
            # Saare labhe hoye shabdan nu ik lari ch jorho
            channel_name = " ".join(text_results).strip()
            
            # Je text nahi labhya taan default ID rakh do
            if not channel_name:
                channel_name = f"Unknown_{stream_id}"
                
            print(f"[OCR SUCCESS] ID {stream_id} -> {channel_name}")
            
            # 4. Tuhade format ch file de aakhir ch line save karni
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{channel_name}] {base_url}\n")
                
            # Temp image delete karo taan jo space na ghure
            os.remove(temp_img)
            
    except Exception:
        if os.path.exists(temp_img):
            os.remove(temp_img)

if __name__ == "__main__":
    print(f"Scanning {START_ID} to {END_ID} and saving directly to {OUTPUT_FILE}...")
    
    # Thread pool thoda ghtaya taan jo OCR memory crash na kare
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_id, range(START_ID, END_ID + 1))
        
    print("Scan complete for this batch!")
    
