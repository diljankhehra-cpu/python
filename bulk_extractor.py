import os
import requests
import subprocess

START_ID = int(os.environ.get("START_ID", 10000))
END_ID = int(os.environ.get("END_ID", 13000))
OUTPUT_FILE = "channels.txt"
MAX_FOLDER_SIZE = 48 * 1024 * 1024 # 48-50 MB ਦੀ ਲਿਮਿਟ

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://mini.allinonereborn.fun/"
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
        # ਸਿਰਫ਼ ਇਹ ਚੈੱਕ ਕਰੋ ਕਿ ਵੈੱਬਸਾਈਟ ਖੁੱਲ੍ਹ ਰਹੀ ਹੈ ਜਾਂ ਨਹੀਂ (Status 200)
        response = requests.get(base_url, headers=HEADERS, allow_redirects=True, timeout=5)
        status = response.status_code
        response.close()
        
        if status != 200:
            return 
            
        target_dir = get_active_folder()
        output_img = f"{target_dir}/{stream_id}.jpg"
        
        # FFmpeg ਸਿੱਧਾ ਲਿੰਕ ਤੋਂ ਵੀਡੀਓ ਖਿੱਚੇਗਾ - ਕੋਈ ਰੋਕ-ਟੋਕ ਨਹੀਂ
        command = [
            'ffmpeg', '-y', 
            '-timeout', '5000000',
            '-headers', f"User-Agent: {HEADERS['User-Agent']}\r\nReferer: {HEADERS['Referer']}\r\n",
            '-i', base_url, 
            '-ss', '00:00:03', 
            '-vframes', '1', 
            output_img
        ]
        
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12)
        
        if result.returncode == 0 and os.path.exists(output_img):
            print(f"[SUCCESS] Captured ID {stream_id} -> Saved in {target_dir}")
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"CHANNEL {stream_id}\n{base_url}\n")
                
    except Exception:
        pass

if __name__ == "__main__":
    print(f"Scanning {START_ID} to {END_ID} with Direct FFmpeg Stream Reader...")
    for s_id in range(START_ID, END_ID + 1):
        process_id(s_id)
    print("All Batches Complete!")
