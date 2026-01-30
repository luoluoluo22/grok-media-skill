
import sys
import json
import time
import os
from pathlib import Path
from curl_cffi import requests

# Add libs to path
current_dir = Path(__file__).parent
libs_path = current_dir.parent / "libs"
sys.path.append(str(libs_path))

try:
    from grok_client import get_auth_context, get_headers
except ImportError:
    print("[-] Error: libs module not found. Path:", libs_path)
    print("[-] Error: shared_utils module not found")
    sys.exit(1)

def generate_image_grok(prompt, ratio=None, count=1):
    cookie_str = get_auth_context()
    if not cookie_str:
        print("[-] Error: Authentication failed (Token not found)")
        return []

    # 强制强化提示词
    safe_prompt = f"Generate an image of {prompt}" if "generate" not in prompt.lower() else prompt
    if ratio:
        safe_prompt = f"{safe_prompt} --aspect {ratio}"
        
    print(f"[*] Sending prompt to Grok: '{safe_prompt}'")
    
    payload = {
        "temporary": True,
        "modelName": "grok-3",
        "message": safe_prompt, 
        "fileAttachments": [],
        "imageAttachments": [],
        "disableSearch": False,
        "enableImageGeneration": True,
        "imageGenerationCount": count,
        "modelMode": "MODEL_MODE_FAST"
    }

    try:
        response = requests.post(
            "https://grok.com/rest/app-chat/conversations/new",
            headers=get_headers(cookie_str),
            json=payload,
            impersonate="chrome133a",
            stream=True,
            timeout=120
        )
        
        image_urls = []
        for line in response.iter_lines():
            if not line: continue
            try:
                line_str = line.decode('utf-8')
                data = json.loads(line_str)
                m_resp = data.get("result", {}).get("response", {}).get("modelResponse", {})
                urls = m_resp.get("generatedImageUrls", [])
                for u in urls:
                    if u not in image_urls: image_urls.append(u)
            except: continue
        
        if not image_urls:
            print("[-] No images returned.")
            return []

        print(f"[+] Generated {len(image_urls)} images. Downloading...")
        
        # Save to current workspace asset dir or specified location
        # Default to a local 'output' folder in the skill 
        save_dir = current_dir.parent / "output"
        save_dir.mkdir(parents=True, exist_ok=True)
        
        local_files = []

        for i, url_path in enumerate(image_urls):
            full_url = f"https://assets.grok.com/{url_path}"
            # Create a simple name
            safe_name = f"grok_{int(time.time())}_{i}.jpg"
            local_path = save_dir / safe_name
            
            try:
                dl_headers = get_headers(cookie_str)
                if "x-statsig-id" in dl_headers:
                    del dl_headers["x-statsig-id"]
                
                r_dl = requests.get(full_url, headers=dl_headers, impersonate="chrome133a", timeout=30)
                if r_dl.status_code == 200:
                    local_path.write_bytes(r_dl.content)
                    print(f" [V] Saved: {local_path}")
                    local_files.append(str(local_path))
            except Exception as e:
                print(f" [X] Download failed: {e}")
                
        return local_files

    except Exception as e:
        print(f"[-] Request failed: {e}")
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate.py <prompt> [ratio]")
        sys.exit(1)
        
    p = sys.argv[1]
    r = sys.argv[2] if len(sys.argv) > 2 else None
    generate_image_grok(p, r)
