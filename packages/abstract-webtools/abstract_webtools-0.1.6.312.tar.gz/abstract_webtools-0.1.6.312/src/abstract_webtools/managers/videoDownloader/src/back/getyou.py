from abstract_webtools import *

import re
import json
import requests
import urllib.parse
from typing import Tuple, List, Dict, Any

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
S = requests.Session()
S.headers.update({"User-Agent": USER_AGENT})
def get_html(url):
    request = requestManager(url)
    return request.source_code
def get_all_js(url=None,html=None):
    if not html:
        html = get_html(url)
    all_js = []
    for line in html.split('.js'):
        all_js.append(f"""{line.split('"')[-1]}.js""")
    return all_js

def fetch_watch_html(video_id: str) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    r = S.get(url, timeout=15)
    r.raise_for_status()
    return r.text


def extract_yt_initial_player_response(html: str) -> dict:
    # common pattern
    m = re.search(r"ytInitialPlayerResponse\s*=\s*(\{.+?\});", html, re.S)
    if not m:
        # fallback: "var ytInitialPlayerResponse = {...};"
        m = re.search(r"var\s+ytInitialPlayerResponse\s*=\s*(\{.+?\});", html, re.S)
    if not m:
        raise RuntimeError("Could not find ytInitialPlayerResponse in page")
    return json.loads(m.group(1))


def find_player_js_url(html: str) -> str:
    # find the base.js/player url - many variants exist; try some common ones
    # look for "jsUrl": "/s/player/....base.js" in the page JSON or script tags
    m = re.search(r'"jsUrl":"(?P<u>[^"]+base\.js)"', html)
    if m:
        u = m.group("u").replace("\\/", "/")
        return urllib.parse.urljoin("https://www.youtube.com", u)
    # fallback: search script tags for /s/player/.../base.js
    m = re.search(r'(/s/player/[\w\d\-_/.]+/base\.js)', html)
    if m:
        return urllib.parse.urljoin("https://www.youtube.com", m.group(1))
    raise RuntimeError("Could not find player base.js URL")


def parse_streaming_data(player_response: dict) -> List[Dict[str, Any]]:
    sd = player_response.get("streamingData", {}) or {}
    formats = sd.get("formats", []) + sd.get("adaptiveFormats", [])
    return formats


# ---------- signature deciphering helpers ----------
def fetch_js(url: str) -> str:
    r = S.get(url, timeout=15)
    r.raise_for_status()
    return r.text


def find_decipher_function_name(js: str) -> str:
    # search for something like: a.set("signature", somefunc(s)) OR "sig||somefunc(s)"
    # common patterns: "functionName=function(a){a=a.split(\"\");...}"
    m = re.search(r"\b([a-zA-Z0-9$]{2,})\s*=\s*function\(\w\)\s*\{\w=\w\.split\(\"\"\)", js)
    if m:
        return m.group(1)
    # other pattern: function abc(a){a=a.split("");
    m = re.search(r"function\s+([a-zA-Z0-9$]{2,})\s*\(\w\)\s*\{\w=\w\.split\(\"\"\)", js)
    if m:
        return m.group(1)
    # newer pattern: e.g. var T7=function(a){a=a.split("");
    m = re.search(r"var\s+([A-Za-z0-9$]{2,})\s*=\s*function\(\w\)\s*\{\w=\w\.split\(\"\"\)", js)
    if m:
        return m.group(1)
##    raise RuntimeError("Decipher function name not found")


def extract_operations(js: str, fn_name: str) -> List[Tuple[str, int]]:
    """
    Find object that contains helper methods and then the function body calling them.
    We'll try to map common ops to ('swap', n), ('reverse', None), ('slice', n) etc.
    """
    # find the function body for fn_name
    pattern = re.compile(rf"{re.escape(fn_name)}\s*=\s*function\(\w\)\s*\{{(.*?)\}}", re.S)
    m = pattern.search(js)
    body = None
    if m:
        body = m.group(1)
    else:
        # try function fn_name(a){...}
        pattern2 = re.compile(rf"function\s+{re.escape(fn_name)}\(\w\)\s*\{{(.*?)\}}", re.S)
        mm = pattern2.search(js)
        if mm:
            body = mm.group(1)
##    if not body:
##        raise RuntimeError("Could not extract function body for decipher fn")

    # find helper object name in body, e.g. var bR={swap:function(a,b){...},reverse:...}; then calls like bR.qd(a,3)
    obj_match = re.search(r"([A-Za-z0-9$]{2,})\.(?:[A-Za-z0-9$]{2,})\(\w,(\d+)\)", body)
    helper_obj = None
    if obj_match:
        helper_obj = obj_match.group(1)

    ops: List[Tuple[str, int]] = []

    # If helper object exists, find its definition and method mapping
    helper_body = ""
    if helper_obj:
        # match object definition: var X={ad:function(a,b){a.splice(0,b);},rd:function(a){a.reverse();},...};
        obj_pattern = re.compile(rf"var\s+{re.escape(helper_obj)}\s*=\s*\{{(.*?)\}};", re.S)
        om = obj_pattern.search(js)
        if om:
            helper_body = om.group(1)
        else:
            # sometimes assigned as X={...}; or X={...}; function calls still use it.
            om2 = re.search(rf"{re.escape(helper_obj)}\s*=\s*\{{(.*?)\}};", js, re.S)
            if om2:
                helper_body = om2.group(1)

    # Build short mapping of helper method names to operation type by heuristics
    method_map = {}
    if helper_body:
        # find each method: abc:function(a,b){a.splice(0,b)}
        for m in re.finditer(r"([A-Za-z0-9$]{2,})\s*:\s*function\([^\)]*\)\s*\{([^\}]+)\}", helper_body):
            name, code = m.group(1), m.group(2)
            code = code.strip()
            if "reverse" in code:
                method_map[name] = ("reverse", None)
            elif ".splice" in code or ".slice" in code:
                # splice likely for removing first n; slice for slicing
                # capture numeric argument from the call site if possible later
                method_map[name] = ("splice", None)
            elif re.search(r"[a-z]\[0\]\s*=\s*[a-z]\[b%[a-z]\.length\]", code) or "var c=" in code and "a[0]" in code:
                method_map[name] = ("swap", None)
            elif "var c=a[0];a[0]=a[b%a.length];a[b%a.length]=c" in code or "var c" in code and "a[b%a.length]" in code:
                method_map[name] = ("swap", None)
            else:
                # fallback
                method_map[name] = ("unknown", None)

    # now scan the body for calls like X.ab(a,3) or a=a.slice(3)
    calls = re.finditer(rf"(?:{re.escape(helper_obj)}\.)?([A-Za-z0-9$]{{2,}})\(\w,?(\d+)?\)", body) if helper_obj else re.finditer(r"([A-Za-z0-9$]{2,})\(\w,?(\d+)?\)", body)
    for c in calls:
        meth = c.group(1)
        num = c.group(2)
        op = method_map.get(meth)
        if op:
            opname, _ = op
            if opname == "splice":
                ops.append(("slice", int(num) if num else 0))
            elif opname == "reverse":
                ops.append(("reverse", None))
            elif opname == "swap":
                ops.append(("swap", int(num) if num else 0))
            else:
                # unknown mapped - treat as noop or try numeric arg
                if num:
                    ops.append(("slice", int(num)))
                else:
                    ops.append(("unknown", None))
        else:
            # direct calls (a=a.split("");a.reverse();a=a.slice(3))
            # check common text around meth name in body
            segment = body
            if re.search(rf"\.{re.escape(meth)}\(", segment):
                # try detect by literal words
                if "reverse" in segment:
                    ops.append(("reverse", None))
                elif "slice" in segment or "splice" in segment:
                    # find number
                    n = c.group(2)
                    ops.append(("slice", int(n) if n else 0))
                else:
                    ops.append(("unknown", None))

    # If still empty, try to extract inline ops: .reverse(), .slice(N), swap pattern
    if not ops:
        if "reverse()" in body:
            ops.append(("reverse", None))
        for m in re.finditer(r"\.slice\((\d+)\)", body):
            ops.append(("slice", int(m.group(1))))
        for m in re.finditer(r"var\s+[a-z]=\w\[0\];\w\[0\]=\w\[(\d+)%\w\.length\];\w\[\1\]=[a-z];", js):
            ops.append(("swap", int(m.group(1))))

##    if not ops:
##        raise RuntimeError("Could not determine decipher operations")

    return ops


def apply_ops(sig: str, ops: List[Tuple[str, Any]]) -> str:
    arr = list(sig)
    for op, val in ops:
        if op == "reverse":
            arr.reverse()
        elif op == "swap":
            n = int(val) if val is not None else 0
            if len(arr):
                i = n % len(arr)
                arr[0], arr[i] = arr[i], arr[0]
        elif op == "slice":
            n = int(val) if val is not None else 0
            arr = arr[n:]
        else:
            # unknown — skip
            pass
    return "".join(arr)


def decipher_signature(js: str, s: str) -> str:
    # find fn name, ops, apply
    fn = find_decipher_function_name(js)
    ops = extract_operations(js, fn)
    return apply_ops(s, ops)


# ---------- main flow ----------
def get_direct_url_for_video(url: str) -> Tuple[str, str]:
    html=get_html(url) 
    all_js = get_all_js(url=url,html=html)
    player_response = extract_yt_initial_player_response(html)
    formats = parse_streaming_data(player_response)
    input(formats)
    # prefer formats with direct url
    for fmt in formats:
        if fmt.get("url"):
            return fmt["url"], fmt.get("qualityLabel") or fmt.get("quality") or fmt.get("mimeType")

    # otherwise parse signatureCipher entries
    # signatureCipher has form: "s=ENC&sp=signature&url=ENCURL" or "cipher=..."
    for fmt in formats:
        sc = fmt.get("signatureCipher") or fmt.get("cipher")
        if not sc:
            continue
        # parse query-string style
        parsed = urllib.parse.parse_qs(sc)
        s = parsed.get("s", [None])[0]
        url = parsed.get("url", [None])[0]
        sp = parsed.get("sp", ["signature"])[0]
        if not s or not url:
            continue

        # fetch player js
        player_js_url = find_player_js_url(html)
        js = fetch_js(player_js_url)
        
        
        # try to decipher
     
        signature = decipher_signature(js, s)

        # append signature param to url
        parsed_url = urllib.parse.urlparse(url)
        q = urllib.parse.parse_qs(parsed_url.query)
        q[sp] = signature
        new_query = urllib.parse.urlencode({k: v if isinstance(v, str) else v for k, v in q.items()}, doseq=True)
        final_url = urllib.parse.urlunparse(parsed_url._replace(query=new_query))
        return final_url, fmt.get("qualityLabel") or fmt.get("mimeType")

    raise RuntimeError("No usable direct URL found (and signature decipher failed)")


# Example usage:
if __name__ == "__main__":
    vid = "0XFudmaObLI"

    url = 'https://www.youtube.com/shorts/6vP02wYh4Ds'
    direct_url, quality = get_direct_url_for_video(url)
    print("Direct URL:", direct_url)
    print("Quality:", quality)

