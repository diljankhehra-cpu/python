import os
import requests
import subprocess

START_ID = int(os.environ.get("START_ID", 10000))
END_ID = int(os.environ.get("END_ID", 10100))
OUTPUT_FILE = "channels.txt"
IMAGE_DIR = "screenshots" # Saariyan photos direct is folder ch jangeeyan

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
            
        # FFmpeg live snapshot
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
    for s_id in range(START_ID, END_ID + 1):
        process_id(s_id)
    print("Batch Complete!")
