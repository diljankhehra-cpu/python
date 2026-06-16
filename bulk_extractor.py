
import os
import requests
import subprocess
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION (GitHub Inputs ton automatic chkkega, nahi taan default use karega) ---
START_ID = int(os.environ.get("START_ID", 666))
END_ID = int(os.environ.get("END_ID", 2000))
OUTPUT_DIR = "captured_channels"
# ---------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def process_id(stream_id):
    output_img = os.path.join(OUTPUT_DIR, f"channel_{stream_id}.jpg")
    
    if os.path.exists(output_img):
        return

    url = f"https://mini.allinonereborn.fun/tata.php?id={stream_id}"
    
    try:
        response = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=5, stream=True)
        real_url = response.url
        response.close()
        
        if "tata.php" in real_url or response.status_code != 200:
            return 
            
        print(f"[FOUND] ID {stream_id} -> Link: {real_url}")
        
        command = [
            'ffmpeg', '-y',
            '-timeout', '5000000',
            '-i', real_url,
            '-ss', '00:00:01', 
            '-vframes', '1',
            output_img
        ]
        
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        
        if result.returncode == 0:
            print(f"[SUCCESS] Saved photo for ID {stream_id}")
        else:
            print(f"[FAILED] FFMPEG couldn't extract from ID {stream_id}")
            
    except requests.exceptions.RequestException:
        pass
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] FFMPEG timed out for ID {stream_id}")
    except Exception as e:
        pass

if __name__ == "__main__":
    print(f"Starting scan from ID {START_ID} to {END_ID}...")
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(process_id, range(START_ID, END_ID + 1))
        
    print("Scan complete!")
