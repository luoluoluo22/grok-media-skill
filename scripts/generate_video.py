
import sys
import json
import time
import base64
import os
from pathlib import Path
from curl_cffi import requests

# Add libs to path
current_dir = Path(__file__).parent
libs_path = current_dir.parent / "libs"
sys.path.append(str(libs_path))
# In this unified skill, generate_image is just next door
sys.path.append(str(current_dir))

try:
    from grok_client import get_auth_context, get_headers
    from generate_image import generate_image_grok
except ImportError:
    print("[-] Error: libs or generate_image module not found")
    print("[-] Error: shared_utils or text-to-image module not found")
    sys.exit(1)

def upload_image(image_input, cookie_str):
    b64_content = ""
    mime = "image/png"
    
    # 逻辑：如果是 URL
    if image_input.startswith("http"):
        print(f"[*] Downloading reference image...")
        try:
            r = requests.get(image_input, impersonate="chrome133a")
            if r.status_code == 200:
                mime = r.headers.get("content-type", "image/png")
                b64_content = base64.b64encode(r.content).decode()
            else:
                print(f"[-] Image download failed: {r.status_code}")
                return None, None
        except Exception as e:
             print(f"[-] Image download error: {e}")
             return None, None
    else:
        # 本地文件
        p = Path(image_input)
        if p.exists():
            print(f"[*] Reading local image: {p.name}...")
            import mimetypes
            mime, _ = mimetypes.guess_type(image_input)
            mime = mime or "image/png"
            b64_content = base64.b64encode(p.read_bytes()).decode()
        else:
            print(f"[-] Local file not found: {image_input}")
            return None, None

    print("[*] Uploading to asset library...")
    payload = {"fileName": "seed.png", "fileMimeType": mime, "content": b64_content}
    
    try:
        # 上传需要特殊的 header
        headers = get_headers(cookie_str, "/upload-file")
        resp = requests.post("https://grok.com/rest/app-chat/upload-file", 
                             headers=headers, 
                             data=json.dumps(payload), impersonate="chrome133a")
        
        if resp.status_code == 200:
            d = resp.json()
            fid = d.get("fileMetadataId")
            furi = d.get("fileUri")
            print(f"[debug] Upload success. ID: {fid}")
            return fid, furi
        else:
            print(f"[-] Upload failed ({resp.status_code})")
    except Exception as e:
        print(f"[-] Upload exception: {e}")
    return None, None

def create_post(file_uri, cookie_str):
    print("[*] Creating Media Post anchor...")
    payload = {"media_url": f"https://assets.grok.com/{file_uri}", "media_type": "MEDIA_POST_TYPE_IMAGE"}
    try:
        resp = requests.post("https://grok.com/rest/media/post/create", 
                             headers=get_headers(cookie_str, "/create"), 
                             json=payload, impersonate="chrome133a")
        if resp.status_code == 200:
            pid = resp.json().get("post", {}).get("id")
            return pid
        else:
            print(f"[-] Create Post failed ({resp.status_code})")
    except Exception as e:
        print(f"[-] Create Post exception: {e}")
    return None

def run_video_gen(post_id, file_id, prompt, cookie_str):
    print(f"[*] Requesting video generation (This takes 1-2 mins)...")
    
    payload = {
        "temporary": True,
        "modelName": "grok-3",
        "message": f"https://grok.com/imagine/{post_id} {prompt} --mode=custom",
        "fileAttachments": [file_id] if file_id else [],
        "toolOverrides": {"videoGen": True},
        "modelMode": "MODEL_MODE_FAST"
    }

    headers = get_headers(cookie_str)
    headers["Referer"] = f"https://grok.com/imagine/{post_id}"

    try:
        response = requests.post(
            "https://grok.com/rest/app-chat/conversations/new",
            headers=headers, json=payload, impersonate="chrome133a", stream=True, timeout=300 
        )
        
        last_p = -1
        v_url = None
        
        for line in response.iter_lines():
            if not line: continue
            try:
                line_str = line.decode('utf-8')
                data = json.loads(line_str)
                
                if "error" in data:
                    print(f"\n[-] API Error: {data['error']}")
                    return

                res = data.get("result", {}).get("response", {}).get("streamingVideoGenerationResponse", {})
                if res:
                    p = res.get("progress", 0)
                    url = res.get("videoUrl")
                    
                    if p > last_p: 
                        print(f" [Generating: {p}%] ", end="\r")
                        last_p = p
                    if url: v_url = url
            except: continue
        
        if v_url:
            print(f"\n[+] Video generated! URL: {v_url}")
            save_dir = Path(os.getcwd()) / "generated_assets"
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = save_dir / f"video_{int(time.time())}.mp4"
            
            print(f"[*] Downloading...")
            dl_headers = get_headers(cookie_str)
            if "x-statsig-id" in dl_headers:
                del dl_headers["x-statsig-id"] 
            
            r_dl = requests.get(f"https://assets.grok.com/{v_url}", headers=dl_headers, impersonate="chrome133a")
            if r_dl.status_code == 200:
                save_path.write_bytes(r_dl.content)
                print(f"[V] Saved video: {save_path}")
                return str(save_path)
            else: print(f"[-] Download failed: {r_dl.status_code}")
        else: 
            print("\n[-] Generation ended without video URL.")
            
    except Exception as e: print(f"\n[-] Video request failed: {e}")
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_video.py <prompt> [image_path_or_ratio]")
        return

    prompt = sys.argv[1]
    arg2 = sys.argv[2] if len(sys.argv) > 2 else None
    
    image_input = None
    ratio = None
    
    def is_ratio(s):
        return s and (":" in s or "--" in s or len(s) < 10)
    
    if arg2:
        if is_ratio(arg2) and not Path(arg2).exists() and not arg2.startswith("http"):
            ratio = arg2
        else:
            image_input = arg2

    cookie = get_auth_context()
    if not cookie:
        print("[-] Error: Authentication failed")
        return

    if not image_input:
        print(f"[*] No base image provided. Generating base image first (Ratio: {ratio or 'Default'})...")
        # Reuse logic from text-to-image
        generated_paths = generate_image_grok(prompt, ratio, count=1)
        if generated_paths:
            image_input = generated_paths[0]
            print(f"[+] Base image generated: {image_input}")
        else:
            print("[-] Failed to generate base image")
            return

    # Now we have image_input, proceed to generate video
    fid, furi = upload_image(image_input, cookie)
    if fid and furi:
        pid = create_post(furi, cookie)
        if pid:
            run_video_gen(pid, fid, prompt, cookie)
        else:
            print("[-] Failed to create post anchor")
    else:
        print("[-] Failed to upload asset")

if __name__ == "__main__":
    main()
