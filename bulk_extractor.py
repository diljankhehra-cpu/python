import os
import requests
import subprocess

START_ID = int(os.environ.get("START_ID", 10000))
END_ID = int(os.environ.get("END_ID", 13000))
OUTPUT_FILE = "channels.txt"
MAX_FOLDER_SIZE = 48 * 1024 * 1024 

# ਸੁਪਰ ਬਾਈਪਾਸ ਹੈਡਰਸ (ਤਾਕਿ ਗਿਟਹੱਬ ਬਲੌਕ ਨਾ ਹੋਵੇ)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,hi;q=0.7",
    "Referer": "https://mini.allinonereborn.fun/",
    "Connection": "keep-alive"
}

def get_folder_size(folder):
    total_size = 0
    if os.path.exists(folder):
        for dirpath, dirnames, filenames in os.walk(folder):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
    return total_size

def get_active_folder():
    part = 1
    while True:
        folder_name = f"screenshots_part{part}"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            return folder_name
        if get_folder_size(folder_name) < MAX_FOLDER_SIZE:
            return folder_name
        part += 1

def process_id(stream_id):
    base_url = f"https://mini.allinonereborn.fun/tata.php?id={stream_id}"
    
    try:
        # Session ਵਰਤ ਕੇ ਕੂਕੀਜ਼ ਆਟੋਮੈਟਿਕ ਸੇਵ ਕਰਾਂਗੇ
        session = requests.Session()
        response = session.get(base_url, headers=HEADERS, allow_redirects=True, timeout=7)
        real_url = response.url
        status = response.status_code
        response.close()
        
        # ਜੇ ਲਿੰਕ ਬਲੌਕ ਹੋ ਕੇ ਵਾਪਸ tata.php 'ਤੇ ਭੇਜ ਰਿਹਾ ਹੈ ਤਾਂ ਸਕਿਪ ਨਾ ਕਰੇ, FFmpeg ਨੂੰ ਚੈੱਕ ਕਰਨ ਦੇਵੇ
        if status != 200:
            return 
            
        target_dir = get_active_folder()
        output_img = f"{target_dir}/{stream_id}.jpg"
        
        # FFmpeg ਕਮਾਂਡ - ਫੁੱਲ ਬਾਈਪਾਸ ਪੈਰਾਮੀਟਰਾਂ ਨਾਲ
        command = [
            'ffmpeg', '-y', 
            '-timeout', '6000000',
            '-headers', f"User-Agent: {HEADERS['User-Agent']}\r\nReferer: {HEADERS['Referer']}\r\n",
            '-redirect_with_list', '1',
            '-i', real_url, 
            '-ss', '00:00:03', 
            '-vframes', '1', 
            output_img
        ]
        
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        
        if result.returncode == 0 and os.path.exists(output_img):
            print(f"[SUCCESS] Captured ID {stream_id} -> Saved in {target_dir}")
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"CHANNEL {stream_id}\n{base_url}\n")
                
    except Exception:
        pass

if __name__ == "__main__":
    print(f"Scanning {START_ID} to {END_ID} with Anti-Block Bypass Enabled...")
    for s_id in range(START_ID, END_ID + 1):
        process_id(s_id)
    print("All Batches with Bypass Complete!")
