import json
import hmac
import hashlib
import base64
import re
import uuid
import random
import string
from datetime import datetime, timezone

import requests

from proto import build_proto, aes_encrypt

HEX_KEY_STR = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
APP_ID = 100067
RELEASE_VER = "OB55"

URL_GUEST_REGISTER = "https://100067.connect.garena.com/api/v2/oauth/guest:register"
URL_TOKEN_GRANT    = "https://100067.connect.garena.com/api/v2/oauth/guest/token:grant"
URL_MAJOR_LOGIN    = "https://loginbp.ppmainecoonghj.com/MajorLogin"
URL_MAJOR_REGISTER = "https://loginbp.ppmainecoonghj.com/MajorRegister"
URL_NEWBIE_CHOICE  = "https://loginbp.ppmainecoonghj.com/ChooseNewbieChoice"

REGION_LANG_FULL = {
    "ME": "ar", "IND": "hi", "ID": "id", "JP": "ja", "VN": "vi",
    "TH": "th", "BD": "bn", "PK": "ur", "TW": "zh", "CIS": "ru",
    "SAC": "es", "BR": "pt", "SG": "en", "US": "en", "EU": "en", "LK": "en",
}

DEVICES = [
    ("Asus ASUS_AI2501_B", "Android OS 12 / API-31 (SP1A.210812.016.C2)", "Adreno (TM) 640"),
    ("Redmi Note 12 Pro",  "Android OS 13 / API-33 (TP1A.220624.014)",   "Adreno (TM) 618"),
    ("Samsung SM-M135F",   "Android OS 13 / API-33 (TP1A.220624.014)",   "Mali-G68"),
    ("Realme RMX3630",     "Android OS 12 / API-31 (SP1A.210812.016)",   "Adreno (TM) 610"),
    ("Vivo V2149",         "Android OS 13 / API-33 (TP1A.220624.014)",   "Adreno (TM) 642L"),
]

FIELD_22 = bytes.fromhex(
    "4747524501010100620200001052aa0d669c6a368f08338060d2ee0690053af84a41edcd3558556ec10f24f4"
    "6c93ac64ca41a16732c46a2cb071246a79b8929032f9e1b6f4ef331bd53cabf29b09b97349a46e9863c0314e"
    "1a0d80819fef8aabf03876b3d037db354a7ccb5c1bce96411fb3753f6f50e44c69c4ed617fa30efb8ffc0517"
    "ff2f636739be1f304d999cfd6fd48bf69454199794c3dc88f55a4bdbd66534d5a061359cdfd1fb680cd37918"
    "df9fdb3cf7d80067b0a3506c90063cf62b2ccec11e23913a2fd7c4ef091331967bb518a5ad1e551146b90821"
    "be800883abadde39d6c80a5d798611466c748f075481806c5842ce45e6bd4e3368ec08fe2ec41ceb880cd862"
    "49eb71693f79f0bccf9e590c3fae12519fe08c7a1905d0927690109e0df28574bb14847225db1a59230e6662"
    "ed7730e15ff9a6c815cb41b420edeada735a4b03e181037c37c2c850257311df2f07b0a56e759372cbd0268e"
    "3f13a292ee4373e38ab5096e0342a5e0d7fec6da2bbc265d74baadd2b24ee4f74862f82c21d6694bac53f8ce"
    "80312a30068a6276a641c19b11d0305c6fe2f531ac7de578b29f543697f5c73663e6f23aa15277b6122dcd4d"
    "4171e38f9ac0b173f39c58416a16c5c1f4a35acd065ce78f449cf538a249339e763272d458e4ed86c976591a"
    "9c066b3a37111e44091eb6b5a795249f3e5145db022a6055f2cc675936391312f688f89627845df222a91156"
    "555225be36f9714a0ba50246d0f003bda3c9c1292ab73b4f79635ddd023218eda93a302d79e023404c143965"
    "44a930b98ed54771aca7fec10d095587685b473e81a9619764fad9256529dcd6e911f4f4629612287d4ee3ec"
    "5389f6ec4ec020b0e2aac017232a9197be9e46239ce690fe5d4872b2e98e651510c971667f3aca8b59f3e9d5"
    "0e43"
)


def _ua():
    return "GarenaMSDK/4.0.44(25028RN03A ;Android 15;id;ID;app 1.132.1 2019121229;)"


def _device():
    model, os_str, gpu = random.choice(DEVICES)
    return {
        "model": model, "os_string": os_str, "gpu": gpu,
        "device_id": "Google|{}".format(uuid.uuid4()),
    }


def _guest_register(password):
    body = json.dumps({
        "app_id": APP_ID, "client_type": 2, "password": password, "source": 2,
    }, separators=(",", ":"))
    sig = hmac.new(HEX_KEY_STR.encode(), body.encode(), hashlib.sha256).hexdigest()
    headers = {
        "User-Agent": _ua(), "Connection": "Keep-Alive",
        "Accept": "application/json", "Accept-Encoding": "gzip",
        "Authorization": "Signature " + sig,
        "Content-Type": "application/json; charset=utf-8",
        "Host": "100067.connect.garena.com",
    }
    r = requests.post(URL_GUEST_REGISTER, headers=headers, data=body, timeout=(3, 8), verify=False)
    if r.status_code == 200:
        j = r.json()
        if j.get("code") == 0 and j.get("data", {}).get("uid"):
            return j["data"]["uid"]
    return None


def _token_grant(uid, password):
    device_id = "02-{}".format(uuid.uuid4())
    body = json.dumps({
        "client_id": APP_ID, "client_secret": HEX_KEY_STR,
        "client_type": 2, "device_id": device_id,
        "password": password, "response_type": "token", "uid": uid,
    }, separators=(",", ":"))
    headers = {
        "User-Agent": _ua(), "Connection": "Keep-Alive",
        "Accept": "application/json", "Accept-Encoding": "gzip",
        "Content-Type": "application/json; charset=utf-8",
        "Host": "100067.connect.garena.com",
    }
    r = requests.post(URL_TOKEN_GRANT, headers=headers, data=body, timeout=(3, 8), verify=False)
    if r.status_code == 200:
        j = r.json()
        if j.get("code") == 0 and "access_token" in j.get("data", {}):
            return j["data"]["access_token"], j["data"]["open_id"]
    return None


def _major_login(access_token, open_id, lang="en"):
    device = _device()
    now_ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    fields = {
        3: now_ts, 4: "free fire", 5: 4, 7: "1.132.1", 8: "2019116753",
        9: device["os_string"], 10: "Handheld", 11: device["model"],
        12: 1280, 13: 720, 14: "240",
        15: "x86-64 SSE3 SSE4.1 SSE4.2 AVX AVX2 | 2400 | 4",
        16: random.choice([5951, 6000, 6100, 5500, 6500]),
        17: device["gpu"], 18: "OpenGL ES 3.1 v1.46",
        19: device["device_id"], 20: "103.0.0.1", 21: lang,
        22: open_id, 23: "4", 24: "Handheld", 25: device["model"],
        26: "ID", 29: access_token, 30: 1,
        41: "Telkomsel", 42: "WIFI",
        92: random.choice([19788, 20000, 21000]),
        93: "android_max", 97: 1, 98: 1, 99: "4", 100: "4",
        104: 77149, 105: 1,
    }
    proto = build_proto(fields)
    payload = aes_encrypt(proto)
    headers = {
        "User-Agent": _ua(), "Accept-Encoding": "deflate, gzip",
        "X-GA-SV": "1789535859", "Authorization": "Bearer " + access_token,
        "X-GA": "v1 1", "ReleaseVersion": RELEASE_VER,
        "Content-Type": "application/octet-stream",
        "X-Unity-Version": "2018.4.12f1",
        "Host": "loginbp.ppmainecoonghj.com",
    }
    r = requests.post(URL_MAJOR_LOGIN, headers=headers, data=payload,
                      verify=False, timeout=(3, 10))
    if r.status_code != 200 or not r.content or len(r.content) < 20:
        return None

    body = r.content
    jwt = None
    text = body.decode('utf-8', errors='ignore')
    m = re.search(r"eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+", text)
    if m:
        jwt = m.group(0)

    account_id = None
    if jwt:
        try:
            p = jwt.split('.')[1]
            p += '=' * (4 - len(p) % 4)
            dec = json.loads(base64.urlsafe_b64decode(p))
            account_id = dec.get('account_id') or dec.get('external_id') or dec.get('uid')
        except Exception:
            pass
    if not account_id:
        nums = re.findall(r'\b\d{10,12}\b', text)
        if nums:
            account_id = nums[0]
    if account_id:
        return {"account_id": str(account_id), "jwt_token": jwt or ""}
    return None


def _major_register(access_token, open_id, uid, password, region, nick, lang):
    keystream = [
        0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,
        0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,
        0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,
        0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,
    ]
    ob = open_id.encode('latin1', errors='ignore')
    field_f14 = bytes((ob[i] ^ keystream[i % len(keystream)]) & 0xFF for i in range(len(ob)))
    payload = {
        1: nick, 2: access_token, 3: open_id,
        5: 102000007, 6: 4, 7: 1, 13: 1,
        14: field_f14, 15: lang, 16: 1, 17: 1, 22: FIELD_22,
    }
    enc = aes_encrypt(build_proto(payload))
    headers = {
        "User-Agent": _ua(), "Accept-Encoding": "deflate, gzip",
        "X-GA-SV": "1789535859", "Authorization": "Bearer",
        "X-GA": "v1 1", "ReleaseVersion": RELEASE_VER,
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2018.4.12f1",
        "Host": "loginbp.ppmainecoonghj.com",
    }
    requests.post(URL_MAJOR_REGISTER, headers=headers, data=enc,
                  verify=False, timeout=(3, 10))
    return _major_login(access_token, open_id, lang)


def _force_region(region, jwt_token):
    try:
        rc = "RU" if region.upper() == "CIS" else region.upper()
        payload = aes_encrypt(build_proto({1: rc}))
        headers = {
            'User-Agent': "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            'Accept-Encoding': "deflate, gzip",
            'X-GA-SV': "1789535859", 'Authorization': "Bearer " + jwt_token,
            'X-GA': "v1 1", 'ReleaseVersion': RELEASE_VER,
            'Content-Type': "application/x-www-form-urlencoded",
            'X-Unity-Version': "2018.4.12f1",
        }
        requests.post(URL_NEWBIE_CHOICE, data=payload, headers=headers,
                      timeout=(3.0, 8.0), verify=False)
    except Exception:
        pass


def _random_nick(prefix):
    prefix = (prefix or "YANZBF")[:6].upper()
    return prefix + "".join(random.choices(string.digits, k=4))


def create_account(region="ID", name_prefix="YANZBF", is_ghost=False):
    password = uuid.uuid4().hex
    uid = _guest_register(password)
    if not uid:
        return None

    tok = _token_grant(uid, password)
    if not tok:
        return None
    access_token, open_id = tok

    lang = REGION_LANG_FULL.get(region.upper(), "en")
    nick = _random_nick(name_prefix)
    login = _major_register(access_token, open_id, uid, password, region, nick, lang)
    if not login:
        return None

    jwt_token = login.get("jwt_token", "")
    if jwt_token and not is_ghost and region.upper() != "BR":
        _force_region(region, jwt_token)

    return {
        "uid": str(uid),
        "password": password,
        "name": nick,
        "account_id": str(login["account_id"]),
        "jwt_token": jwt_token,
        "access_token": access_token,
        "open_id": open_id,
        "region": "GHOST" if is_ghost else region.upper(),
        "is_ghost": is_ghost,
        "status": "success",
    }