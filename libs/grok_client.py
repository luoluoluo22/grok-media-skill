
import json
import uuid
import base64
import random
import string
import os
from pathlib import Path

# 配置路径 (指向 shared_utils 平级的 data 目录，或者用户指定的目录)
# 暂时假设 data 目录在 shared_utils/data
CURRENT_DIR = Path(__file__).parent
DATA_DIR = CURRENT_DIR / "data"
TOKEN_FILE = DATA_DIR / "token.json"
SETTING_FILE = DATA_DIR / "setting.toml"

def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_cf_clearance():
    if not SETTING_FILE.exists(): return ""
    try:
        import toml
        data = toml.load(SETTING_FILE)
        cf = data.get("grok", {}).get("cf_clearance", "")
        if cf and not cf.startswith("cf_clearance="):
            cf = f"cf_clearance={cf}"
        return cf
    except: return ""

def _generate_statsig_id():
    import base64
    import random
    import string
    def rand_str(length, letters_only=True):
        chars = string.ascii_lowercase if letters_only else string.ascii_lowercase + string.digits
        return ''.join(random.choices(chars, k=length))
    
    if random.choice([True, False]):
        rand = rand_str(5, letters_only=False)
        msg = f"e:TypeError: Cannot read properties of null (reading 'children['{rand}']')"
    else:
        rand = rand_str(10)
        msg = f"e:TypeError: Cannot read properties of undefined (reading '{rand}')"
    return base64.b64encode(msg.encode()).decode()

def get_sso_jwt():
    if not TOKEN_FILE.exists(): return None
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for cat in ["ssoNormal", "ssoSuper"]:
                if cat in data and data[cat]:
                    for jwt, info in data[cat].items():
                        if info.get("status") == "active": return jwt
    except: return None

def get_headers(cookie_str, path="/"):
    content_type = "text/plain;charset=UTF-8" if "upload-file" in path else "application/json"
    
    # 动态获取配置
    import toml
    try:
        data = toml.load(SETTING_FILE)
        grok_cfg = data.get("grok", {})
        dynamic_statsig = grok_cfg.get("dynamic_statsig", True)
        statsig = _generate_statsig_id() if dynamic_statsig else grok_cfg.get("x_statsig_id")
        ua = grok_cfg.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")
    except:
        statsig = _generate_statsig_id()
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

    headers = {
        "User-Agent": ua,
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Content-Type": content_type,
        "x-statsig-id": statsig,
        "x-xai-request-id": str(uuid.uuid4()),
        "x-traceparent": "00-e172a5a544b6c39f993d39c06346b0a6-577660633c5e0da6-00", # Use a dummy or dynamic
        "Cookie": cookie_str,
        "Referer": "https://grok.com/",
        "Origin": "https://grok.com",
        "Priority": "u=1, i",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="133", "Google Chrome";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }
    return headers

def get_full_cookie():
    if not SETTING_FILE.exists(): return ""
    try:
        import toml
        data = toml.load(SETTING_FILE)
        return data.get("grok", {}).get("cookie", "")
    except: return ""

def get_auth_context():
    """获取完整的认证需要的上下文 (Cookie)"""
    # 优先尝试从 setting.toml 获取完整 Cookie
    full_cookie = get_full_cookie()
    if full_cookie:
        return full_cookie
        
    jwt = get_sso_jwt()
    if not jwt:
        return None
    
    cookie = f"sso-rw={jwt}; sso={jwt}"
    cf = get_cf_clearance()
    if cf: cookie = f"{cookie}; {cf}"
    return cookie
