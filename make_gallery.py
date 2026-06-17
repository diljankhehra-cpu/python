import os

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Diljan Channel Gallery</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #121212; color: white; text-align: center; margin: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; padding: 20px; }}
        .card {{ background: #1e1e1e; padding: 10px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }}
        img {{ width: 100%; border-radius: 4px; background: #000; height: auto; }}
        h3 {{ margin: 10px 0 0 0; font-size: 14px; color: #00ffcc; }}
    </style>
</head>
<body>
    <h1>Diljan's Live Channel Gallery</h1>
    <div class="grid">
        {cards}
    </div>
</body>
</html>
"""

def generate():
    cards_html = ""
    folders = sorted([f for f in os.listdir('.') if f.startswith('screenshots_part') and os.path.isdir(f)])
    
    for folder in folders:
        files = sorted([f for f in os.listdir(folder) if f.endswith(('.jpg', '.jpeg', '.png'))])
        for file in files:
            stream_id = file.split('.')[0]
            img_path = f"{folder}/{file}"
            cards_html += f"""
            <div class="card">
                <img src="{img_path}" alt="ID {stream_id}" loading="lazy">
                <h3>ID: {stream_id}</h3>
            </div>
            """
            
    final_html = HTML_TEMPLATE.format(cards=cards_html if cards_html else "<p>No photos found</p>")
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    print("Gallery generated!")

if __name__ == "__main__":
    generate()
