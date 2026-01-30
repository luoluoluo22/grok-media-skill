
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
    def rand_str(length):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    msg = f"e:TypeError: Cannot read properties of null (reading 'children['{rand_str(5)}']')"
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Content-Type": content_type,
        "x-statsig-id": _generate_statsig_id(),
        "x-xai-request-id": str(uuid.uuid4()),
        "Cookie": cookie_str,
        "Referer": "https://grok.com/imagine",
        "Origin": "https://grok.com",
        "Priority": "u=1, i"
    }
    return headers

def get_auth_context():
    """获取完整的认证需要的上下文 (Cookie)"""
    jwt = get_sso_jwt()
    if not jwt:
        return None
    
    cookie = f"sso-rw={jwt}; sso={jwt}"
    cf = get_cf_clearance()
    if cf: cookie = f"{cookie}; {cf}"
    return cookie
