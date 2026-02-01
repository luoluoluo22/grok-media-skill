
import sys
import json
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
    print("[-] Error: libs module not found.")
    sys.exit(1)

def test_chat(prompt="Hi"):
    cookie_str = get_auth_context()
    if not cookie_str:
        print("[-] Error: Authentication failed (Token not found)")
        return

    # 从 setting.toml 读取代理
    from grok_client import SETTING_FILE
    proxy = None
    try:
        import toml
        data = toml.load(SETTING_FILE)
        proxy = data.get("grok", {}).get("proxy_url")
    except: pass
    
    proxies = {"http": proxy, "https": proxy} if proxy else None

    print(f"[*] Testing Grok Chat with prompt: '{prompt}'")
    print(f"[*] Using Proxy: {proxy}")
    
    payload = {
        "temporary": False,
        "modelName": "grok-4-1-thinking-1129",
        "message": prompt,
        "fileAttachments": [],
        "imageAttachments": [],
        "disableSearch": False,
        "enableImageGeneration": True,
        "returnImageBytes": False,
        "returnRawGrokInXaiRequest": False,
        "enableImageStreaming": True,
        "imageGenerationCount": 2,
        "forceConcise": False,
        "toolOverrides": {},
        "enableSideBySide": True,
        "sendFinalMetadata": True,
        "customPersonality": "Respond briefly and directly, using as few words as possible.",
        "isReasoning": False,
        "disableTextFollowUps": False,
        "responseMetadata": {
            "modelConfigOverride": {"modelMap": {}},
            "requestModelDetails": {"modelId": "grok-4-1-thinking-1129"}
        },
        "disableMemory": False,
        "forceSideBySide": False,
        "modelMode": "MODEL_MODE_AUTO",
        "isAsyncChat": False,
        "deviceEnvInfo": {
            "darkModeEnabled": True,
            "devicePixelRatio": 1,
            "screenWidth": 2560,
            "screenHeight": 1440,
            "viewportWidth": 937,
            "viewportHeight": 456
        }
    }

    try:
        response = requests.post(
            "https://grok.com/rest/app-chat/conversations/new",
            headers=get_headers(cookie_str),
            json=payload,
            impersonate="chrome133a", # Use Chrome for better TLS fingerprint
            stream=True,
            timeout=120,
            proxies=proxies
        )
        
        if response.status_code != 200:
            print(f"[-] HTTP Error: {response.status_code}")
            print(f"[-] Response: {response.text[:500]}")
            return

        full_text = ""
        is_thinking = False
        print("[*] Receiving response stream...")
        
        for line in response.iter_lines():
            if not line: continue
            line_str = line.decode('utf-8')
            
            try:
                data = json.loads(line_str)
                res_obj = data.get("result", {}).get("response", {})
                
                # 检查是否在思考
                current_thinking = res_obj.get("isThinking", False)
                if current_thinking and not is_thinking:
                    print("\n[Thinking] ", end="", flush=True)
                    is_thinking = True
                elif not current_thinking and is_thinking:
                    print("\n[Answer] ", end="", flush=True)
                    is_thinking = False

                # 提取 Token (参考 grok2api 逻辑)
                token = res_obj.get("token")
                if token and isinstance(token, str):
                    print(token, end="", flush=True)
                    full_text += token
                
                # 检查是否结束
                if res_obj.get("isComplete"):
                    print("\n[+] Response complete.")
                    break
                    
            except json.JSONDecodeError:
                if "<html" in line_str.lower():
                    print(f"\n[!] Cloudflare Verification Detected (HTML Response)")
                    # print(f"DEBUG RAW: {line_str[:200]}...")
                    break
                continue

        if not full_text:
            print("\n[-] No content parsed from stream.")
        else:
            print(f"\n[V] Success! Total characters: {len(full_text)}")

    except Exception as e:
        print(f"\n[-] Request failed: {e}")

if __name__ == "__main__":
    test_p = "你好，请确认你的模型版本，并简单打个招呼。"
    if len(sys.argv) > 1:
        test_p = " ".join(sys.argv[1:])
    test_chat(test_p)
