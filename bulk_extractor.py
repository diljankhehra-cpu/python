import os
import requests
import subprocess
import zipfile
from concurrent.futures import ThreadPoolExecutor

START_ID = int(os.environ.get("START_ID", 666))
END_ID = int(os.environ.get("END_ID", 700))
OUTPUT_FILE = "channels.txt"
IMAGE_DIR = "temp_screenshots" # Pehla temporary folder ch photos rkhange
ZIP_FILE_NAME = "channel_screenshots.zip" # Final zip file da naam

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def process_id(stream_id):
    base_url = f"https://mini.allinonereborn.fun/tata.php?id={stream_id}"
    output_img = f"{IMAGE_DIR}/{stream_id}.jpg"
    
    try:
        response = requests.get(base_url, headers=HEADERS, allow_redirects=True, timeout=5, stream=True)
        real_url = response.url
        response.close()
        
        if "tata.php" in real_url or response.status_code != 200:
            return 
            
        # FFmpeg snapshot (2nd second)
        command = [
            'ffmpeg', '-y', '-timeout', '4000000',
            '-i', real_url, '-ss', '00:00:02', '-vframes', '1', output_img
        ]
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12)
        
        if result.returncode == 0 and os.path.exists(output_img):
            print(f"[SUCCESS] Captured ID {stream_id}")
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"CHANNEL {stream_id}\n{base_url}\n")
                
    except Exception:
        pass

if __name__ == "__main__":
    print(f"Generating screenshots from {START_ID} to {END_ID}...")
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(process_id, range(START_ID, END_ID + 1))
        
    # --- ZIP FILE MAKER LOGIC ---
    print("Zipping files...")
    # 'a' (append) mode rkhya hai taan jo puraani zip ch nvian photos add hundiyan rehn
    with zipfile.ZipFile(ZIP_FILE_NAME, 'a', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(IMAGE_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                # Zip de andar direct image file pao bina folder structure de
                zipf.write(file_path, file)
                # Compress hon ton baad temporary photo delete kar do
                os.remove(file_path)
                
    # Temporary folder nu mitao            
    try:
        os.rmdir(IMAGE_DIR)
    except:
        pass
        
    print(f"Batch Complete! Zip file updated: {ZIP_FILE_NAME}")
