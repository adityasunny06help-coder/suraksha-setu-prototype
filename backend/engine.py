"""Suraksha Setu v4 — detector engine ka Python port.

js/engine.js ka faithful port hai: wahi constants, wahi rules, wahi scores.
Cross-language parity gate: 6 built-in samples par Python bhi wahi scores deta
hai jo JavaScript deta hai (85/0/85/85/30/0) — tests/test_engine_parity.py dekho.

Dhyaan: ye module user ke diye URL ko KABHI fetch nahi karta — sirf text
analysis hai. Live signal (RDAP) rdap.py me hai, woh bhi sirf domain par.
"""
import re
from urllib.parse import urlparse

A = re.ASCII  # JS ke \d / \w hamesha ASCII hote hain — Python me bhi wahi rakho

OFFICIAL = {
    "sbi": ["sbi.bank.in", "sbi.co.in", "onlinesbi.sbi"], "hdfc": ["hdfc.bank.in", "hdfcbank.com"], "hdfcbank": ["hdfc.bank.in", "hdfcbank.com"],
    "icici": ["icici.bank.in", "icicibank.com"], "axis": ["axisbank.com", "axis.bank.in"], "kotak": ["kotak.bank.in", "kotak.com"],
    "paytm": ["paytm.com", "paytmbank.com"], "phonepe": ["phonepe.com"], "amazon": ["amazon.in", "amazon.com"], "flipkart": ["flipkart.com"],
    "irctc": ["irctc.co.in"], "uidai": ["uidai.gov.in"], "aadhaar": ["uidai.gov.in"], "npci": ["npci.org.in"], "indiapost": ["indiapost.gov.in"],
    "parivahan": ["parivahan.gov.in"], "google": ["google.com"], "lic": ["licindia.in"], "epfo": ["epfindia.gov.in"], "jio": ["jio.com"], "airtel": ["airtel.in"], "pnb": ["pnbindia.in"], "bankofbaroda": ["bankofbaroda.in"], "canara": ["canarabank.com", "canarabank.in"], "unionbank": ["unionbankofindia.co.in"], "meesho": ["meesho.com"], "myntra": ["myntra.com"], "delhivery": ["delhivery.com"], "dtdc": ["dtdc.in"], "bluedart": ["bluedart.com"],
    "paypal": ["paypal.com", "paypal.me"], "whatsapp": ["whatsapp.com", "wa.me"], "microsoft": ["microsoft.com", "microsoftonline.com", "live.com", "outlook.com"], "netflix": ["netflix.com"], "instagram": ["instagram.com"], "telegram": ["telegram.org", "telegram.me", "t.me"],
}
ALL_OFFICIAL = [d for v in OFFICIAL.values() for d in v]
BRANDS = list(OFFICIAL.keys())
SHORTENERS = ["bit.ly", "tinyurl.com", "cutt.ly", "rb.gy", "t.co", "goo.gl", "tiny.cc", "is.gd", "shorturl.at", "rebrand.ly", "s.id", "ow.ly", "buff.ly"]
FREEHOST = ["vercel.app", "netlify.app", "firebaseapp.com", "web.app", "github.io", "gitlab.io", "000webhostapp.com", "weebly.com", "blogspot.com", "wixsite.com", "glitch.me", "surge.sh", "pages.dev", "workers.dev", "ngrok.io", "ngrok-free.app", "trycloudflare.com", "serveo.net", "appspot.com", "azurewebsites.net", "herokuapp.com", "onrender.com", "railway.app", "fly.dev", "hf.space", "streamlit.app", "blogspot.in"]
TLD1 = ["top", "zip", "cfd", "sbs", "bond", "cyou", "icu", "click", "quest", "surf", "cam", "buzz", "rest", "mov", "tk", "ml", "ga", "cf", "gq"]
TLD2 = ["xyz", "online", "site", "shop", "live", "info", "biz", "club", "store"]
SENS = ["login", "signin", "sign-in", "verify", "kyc", "otp", "auth", "secure", "update", "recovery", "password", "wallet", "pay", "payment", "refund", "bank", "account", "challan", "bill", "checkout"]
HANDLES = ["okaxis", "okhdfcbank", "okhdfc", "okicici", "oksbi", "ybl", "ibl", "axl", "paytm", "ptyes", "ptaxis", "pthdfc", "apl", "yapl", "rapl", "upi", "sbi", "hdfcbank", "icici", "axisbank", "kotak", "okbizaxis", "rajgovhdfcbank"]
SUFFIX2 = ["co.in", "bank.in", "gov.in", "ac.in", "org.in", "net.in", "com.in", "firm.in", "gen.in", "ind.in", "co.uk", "com.au"]

URL_RE = re.compile(r"((https?://|www\.)[^\s]+|[\w\-]+(\.[\w\-]+)+\.[a-z]{2,}(:\d+)?(/[^\s]*)?)", re.I | A)
VPA_RE = re.compile(r"[\w.\-]{2,}@[a-zA-Z]{2,}[\w]*(?![\w]|\.[a-zA-Z])", A)

SAMPLES = ["https://sbi-kyc-verify.top/login", "https://www.sbi.bank.in", "https://meesho-offer-free.vercel.app/login",
           "I am CBI officer. A parcel with drugs in your name is seized. You are under digital arrest. Stay on WhatsApp video call, tell no one, transfer money to RBI verification account.",
           "9876543210", "https://www.pnbindia.in"]
EXPECTED_SCORES = [85, 0, 85, 85, 30, 0]


def lev(a, b):
    m, n = len(a), len(b)
    d = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        d[i][0] = i
    for j in range(n + 1):
        d[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1] else 1))
    return d[m][n]


def registrable(host):
    parts = host.split(".")
    if len(parts) <= 2:
        return host
    last2 = ".".join(parts[-2:])
    if last2 in SUFFIX2:
        return ".".join(parts[-3:])
    return last2


def sld_of(host):
    return registrable(host).split(".")[0]


def is_official(host):
    return any(host == d or host.endswith("." + d) for d in ALL_OFFICIAL)


def official_for(brand, host):
    return any(host == d or host.endswith("." + d) for d in OFFICIAL.get(brand, []))


def score_url(raw, in_message):
    score = 0
    reasons = []
    hard = 0

    def add(p, r):
        nonlocal score
        if p > 0:
            score += p
            reasons.append([p, r])

    txt = raw.strip()
    if re.match(r"^(data|javascript|blob|file):", txt, re.I):
        return {"score": 90, "reasons": [[90, "Dangerous scheme (data:/javascript:) — asli website aisi nahi hoti"]], "hard": 1, "official": False, "host": ""}
    try:
        u = urlparse(txt if re.match(r"^https?://", txt, re.I) else "https://" + txt)
        host = (u.hostname or "").lower().rstrip(".")
        if not host:
            raise ValueError("no host")
        port = u.port  # invalid port par ValueError — JS ka new URL bhi throw karta hai
    except Exception:
        return {"score": 20, "reasons": [[20, "Link samajh nahi aaya — aise link par tap mat karo"]], "hard": 0, "official": False, "host": ""}
    pathname = u.path or ""
    search = ("?" + u.query) if u.query else ""
    path = (pathname + " " + search).lower()
    username = u.username or ""
    scheme = u.scheme.lower()
    official = is_official(host)
    if official:
        return {"score": 0, "reasons": [[0, "Official domain match: " + host + " — whitelist me hai"]], "hard": 0, "official": True, "host": host, "sensitive": any(w in path for w in SENS)}
    if re.search(r"\.(apk|exe|scr|msi)(\?|$)", pathname, re.I):
        hard = 1
        reasons.append([85, "Seedha APK/EXE download — bank/payment app aise install nahi hota"])
    is_ip = bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host, A)) or (":" in host) or bool(re.match(r"^0x[0-9a-f]+$", host, re.I))
    brand_in_host = [b for b in BRANDS if b in host]
    brand_in_user = bool(username) and any(b in username.lower() for b in BRANDS)
    sensitive = [w for w in SENS if w in path]
    # Hard rules
    if brand_in_user:
        hard = 1
        reasons.append([85, "@ wala trick: asli site @ ke BAAD wala hissa hai, pehle brand ka naam sirf dhokha hai"])
    if is_ip and (brand_in_host or brand_in_user or sensitive):
        hard = 1
        reasons.append([85, "Brand/login wala page seedha IP address par — asli bank IP par nahi chalta"])
    for b in brand_in_host:
        if not official_for(b, host):
            hard = 1
            reasons.append([85, "Brand impersonation: '" + b + "' naam is domain me hai, lekin ye uska official domain NAHI hai (official: " + ", ".join(OFFICIAL[b]) + ")"])
    sld = sld_of(host)
    if not official:
        for b in BRANDS:
            if sld != b and 1 <= lev(sld, b) <= 2 and len(b) >= 4:
                hard = 1
                reasons.append([85, "Typosquat domain: '" + sld + "' asli brand '" + b + "' ki nakli spelling lagti hai"])
    if ("xn--" in host) or any(ord(c) > 0x7F for c in host):
        if brand_in_host or sensitive or lev(re.sub(r"^xn--", "", sld), "sbi") <= 3:
            hard = 1
            reasons.append([85, "Punycode/homograph domain + sensitive page — asli brand ki nakal ho sakti hai"])
        else:
            add(25, "Punycode (xn--) domain — akshar dhokha de sakte hain")
    freehost = next((f for f in FREEHOST if host == f or host.endswith("." + f)), None)
    if freehost and (brand_in_host or "login" in path or "signin" in path):
        hard = 1
        reasons.append([85, "Free-hosting (" + freehost + ") par brand ka login page — asli company aise host nahi karti"])
    # Additive
    add(15, "Domain pehchana nahi gaya — kisi official list me nahi hai")
    if is_ip:
        add(35, "Host domain nahi, seedha IP address hai")
    if username:
        add(30, "URL me @ hai — browser @ ke baad wali site kholta hai")
    if host in SHORTENERS:
        add(20, "Shortened link — asli destination chhupa hai")
    if freehost:
        add(20, "Free-hosting/tunnel domain (" + freehost + ")")
    tld = host.split(".")[-1]
    if tld in TLD1:
        add(18, "High-risk sasta TLD (." + tld + ") — scam sites me bahut common")
    elif tld in TLD2:
        add(8, "Kam-bharose wala TLD (." + tld + ")")
    if scheme == "http":
        add(15 if sensitive else 5, "HTTP (bina lock) par login/payment wala page" if sensitive else "HTTP hai, HTTPS nahi")
    if port:
        add(15, "Non-standard port (" + str(port) + ")")
    ln = len(txt)
    add(15 if ln > 110 else 10 if ln > 75 else 5 if ln > 53 else 0, "Link bahut lamba hai (" + str(ln) + " characters)")
    reg = registrable(host)
    subs = 0 if host == reg else len(host[:len(host) - len(reg) - 1].split("."))
    add(15 if subs >= 4 else 10 if subs == 3 else 5 if subs == 2 else 0, "Bahut zyada subdomains (" + str(subs) + ") — asli domain chhupaya gaya hai")
    hy = sld.count("-")
    add(10 if hy >= 2 else 5 if hy == 1 else 0, "Domain me zyada hyphens")
    dig = len(re.findall(r"[0-9]", sld))
    if dig >= 3 or len(sld) > 20:
        add(10, "Domain me zyada digits / bahut lamba naam")
    add(15 if len(sensitive) >= 2 else 8 if len(sensitive) == 1 else 0, "Path me sensitive words: " + ", ".join(sensitive[:3]))
    if in_message:
        add(10, "Ye link ek message ke andar aaya hai — unsolicited link extra risky hota hai")
    if sensitive:
        score = max(score, 35)
    if sensitive and scheme == "http":
        score = max(score, 55)
    if hard:
        score = max(score, 85)
    return {"score": min(score, 100), "reasons": reasons, "hard": hard, "official": False, "host": host, "sensitive": len(sensitive) > 0}


def score_vpa(vpa):
    reasons = []
    score = 0
    hard = 0
    m = re.match(r"^([\w.\-]{2,})@([a-z0-9]{2,})$", vpa.lower(), A)
    if not m:
        return {"score": 20, "reasons": [[20, "UPI ID ka format sahi nahi lag raha"]], "hard": 0}
    local, handle = m.group(1), m.group(2)
    look = None
    if handle not in HANDLES:
        look = next((h for h in HANDLES if h != handle and 1 <= lev(handle, h) <= 2 and len(h) >= 6), None)
    brand_name = next((b for b in BRANDS if b in local), None)
    lure = next((w for w in ("refund", "cashback", "prize", "reward") if w in local), None)
    brand_local = brand_name or lure
    if look:
        score = max(score + 40, 55)
        reasons.append([40, "Handle '@" + handle + "' asli '@" + look + "' se ek akshar alag hai — nakli handle ho sakta hai"])
    if brand_name:
        score += 20
        reasons.append([20, "UPI naam me brand word hai ('" + local + "') — koi bhi aisa naam bana sakta hai, ye proof nahi hai"])
    if lure and not look:
        score = max(score + 20, 55)
        reasons.append([20, "UPI naam me lure word hai ('" + lure + "') — paisa paane ka jhansa dene wale naam scam me aam hain, pehle verify karo"])
    if brand_local and (handle not in HANDLES or look):
        hard = 1
        reasons.append([85, "Brand wala naam + galat/nakli handle — UPI scam pattern"])
    if handle not in HANDLES and not look:
        score = max(score + 15, 35)
        reasons.append([15, "Handle '@" + handle + "' jaane-pehchane bank/app handles me nahi hai — payee verify nahi ho paya"])
    if handle in HANDLES and not score:
        score = 20
        # JS yahan [[20], str][1] push karta hai = sirf string (points nrm me 0 bante hain) — waisa hi rakha hai
        reasons.append("Handle asli list me hai, LEKIN isse payee asli sabit nahi hota — app me dikhne wala NAAM apne jaankari se match karo")
    if hard:
        score = max(score, 85)
    return {"score": min(score, 100), "reasons": reasons, "hard": hard}


def score_message(text):
    t = text.lower()
    reasons = []
    score = 0
    hard = 0

    def has(*ws):
        return any(w in t for w in ws)

    clusters = []
    if has("digital arrest", "डिजिटल अरेस्ट", "digital custody"):
        hard = 1
        clusters.append([85, "DIGITAL ARREST scam — CBI/Police/Customs kabhi video call par arrest nahi karte (I4C advisory)"])
    auth_sig = sum([
        has("cbi", "ed officer", "customs officer", "police officer", "rbi officer", "enforcement directorate"),
        has("video call", "whatsapp video", "skype call"),
        has("parcel", "drugs", "money laundering", "seized"),
        has("tell no one", "kisi ko mat bata", "secret", "गुप्त"),
        has("verification account", "transfer karo", "transfer now"),
    ])
    if not hard and auth_sig >= 3:
        hard = 1
        clusters.append([85, "Digital-arrest pattern: officer ka daava + video call + parcel/drugs ya secrecy + paisa transfer"])
    if re.search(r"pin[^.]{0,50}(to receive|receive karne|receive karo|paise paane|refund paane)|(receive|refund)[^.]{0,50}(enter|daalo|share|type)[^.]{0,25}(pin|otp)", t) or has("collect request approve karke pin", "approve the collect request and enter") or (has("collect request") and has("pin", "upi pin")):
        hard = 1
        clusters.append([85, "PIN daal kar paisa RECEIVE nahi hota — UPI PIN sirf paisa DENE ke liye hota hai (NPCI niyam). Ye pakka scam hai"])
    if has("prepaid task", "pre-paid task") or re.search(r"(deposit|jama)[^.]{0,40}(earn|profit|wapas.*double|get ₹|get rs)", t) or re.search(r"(deposit|jama)[^.]{0,60}(task|like|telegram)|(task|like)[^.]{0,60}(deposit|jama)", t):
        hard = 1
        clusters.append([85, "Task scam: pehle paise jama karwa kar 'profit' ka jhansa — paisa gaya to wapas nahi aata"])
    if (has("fee", "charge", "deposit") and has("withdraw", "unfreeze")) or (has("fee", "charge", "deposit") and has("release your") and has("profit", "balance", "funds", "money", "amount", "investment", "crypto", "wallet", "earning")):
        hard = 1
        clusters.append([85, "Paisa nikaalne ke liye pehle fee — investment scam ki pakki pehchan"])
    if has("intimate video", "private video viral", "video viral kar dunga", "sextortion"):
        hard = 1
        clusters.append([85, "Sextortion/blackmail pattern — paisa mat do, 1930 par report karo"])
    cluster = 0
    cluster_name = ""

    def set_c(p, r):
        nonlocal cluster, cluster_name
        if p > cluster:
            cluster, cluster_name = p, r

    if has("kyc") and has("expire", "expired", "block", "update", "pending", "suspend", "बंद", "ब्लॉक"):
        set_c(35, "KYC scam pattern — bank KYC kabhi SMS/WhatsApp link se nahi karte (RBI)")
    if has("parcel", "courier", "package") and has("drugs", "seized", "customs fee", "customs duty", "clearance"):
        set_c(30, "Courier/customs scam pattern — parcel ke naam par fee vasuli")
    if has("electricity", "bijli", "बिजली") and has("disconnect", "cut", "kaat", "डिस्कनेक्ट"):
        set_c(35, "Bijli disconnect scam — board kabhi aise message se turant paisa nahi maangta")
    if has("challan") and has("pay", "link", "http"):
        set_c(30, "Challan scam pattern — asli challan sirf parivahan.gov.in par bharo")
    if has("customer care", "customercare", "helpline number") and has("call", "number", "संपर्क"):
        set_c(25, "Fake customer-care pattern — number hamesha official app/site se lo")
    if has("loan") and has("processing fee", "approval fee", "pay first", "upfront"):
        set_c(35, "Loan scam — asli loan pehle fee nahi maangta")
    if has("guaranteed return", "guaranteed profit", "double money", "paisa double", "100% profit", "daily profit"):
        set_c(30, "Guaranteed/double profit — aisi guarantee sirf scam deta hai")
    if has("like karo", "like videos", "youtube video like", "telegram group", "telegram channel") and has("earn", "daily", "₹", "rs ", "kamao", "kamai"):
        set_c(25, "Task/job scam pattern — like karke hazaron kamai ka jhansa")
    if cluster:
        clusters.append([cluster, cluster_name])
    score = cluster

    def cross(c, p, r):
        nonlocal score
        if c:
            score += p
            reasons.append([p, r])

    cross(bool(re.search(r"(share|batao|send|enter|daalo|type)[^.]{0,25}(otp|pin|cvv|password)", t)) or has("otp batao", "share otp", "otp share"), 25, "OTP/PIN/CVV maangna — bank ya koi officer kabhi nahi maangta")
    cross(bool(re.search(r"(share|sharing|batao|send|daalo)[^.]{0,30}(6-digit code|verification code)", t)), 25, "Verification code maangna — asli company apna bheja hua code kabhi share karne ko nahi kehti")
    apk_word = bool(re.search(r"\bapk\b", t, A))
    ss_tool = has("anydesk", "teamviewer", "quicksupport", "screen share")
    cross((has("install", "download karo") or apk_word) and (has("app") or apk_word or ss_tool), 35 if ss_tool else 20, "App/APK install ya screen-share karwana — phone ka control dena hai")
    cross(has("tonight", "today", "within 2 hour", "within few hour", "last chance", "blocked today", "expire ho jayega", "तुरंत", "आज ही") or bool(re.search(r"(^|[^a-zA-Z])(abhi|turant)(?![a-zA-Z])", t)), 10, "Turant/band hone ka pressure — sochne ka time na dena scam ki chaal hai")
    cross(has("tell no one", "kisi ko mat batao", "secret rakho", "गुप्त रखो"), 10, "Chhupane ko kehna — asli authority kabhi nahi kehti")
    cross(has("lottery", "won", "prize", "cashback milega", "free gift", "inaam", "इनाम"), 10, "Lottery/prize/cashback ka lalach")
    cross(has("electricity officer", "officer ka number", "call karo") and bool(re.search(r"[0-9]{10}", t)), 10, "Officer ka personal mobile number — official kaam personal number se nahi hota")
    all_reasons = clusters + reasons
    if hard:
        score = max(score, 85)
    return {"score": min(score, 100), "reasons": all_reasons, "hard": hard}


def score_phone(raw):
    d = re.sub(r"[^0-9]", "", raw or "")
    if len(d) == 12 and d.startswith("91"):
        d = d[2:]
    if len(d) == 11 and d.startswith("0"):
        d = d[1:]
    if re.match(r"^(1800|000800)", d):
        return {"score": 10, "reasons": [[10, "Toll-free number (1800) — companies ke liye hota hai, phir bhi OTP/PIN kabhi mat do"]], "hard": 0, "kind": "Phone Number"}
    if d.startswith("140"):
        return {"score": 45, "reasons": [[45, "140 series = telemarketing/promo number hai — bank ya sarkar is series se faisla wali call nahi karte"]], "hard": 0, "kind": "Phone Number"}
    if d.startswith("160"):
        return {"score": 20, "reasons": [[20, "160 series = service/transactional calls ke liye reserved hai — phir bhi caller ki baat official app se verify karo"]], "hard": 0, "kind": "Phone Number"}
    if re.fullmatch(r"[6-9][0-9]{9}", d):
        return {"score": 30, "reasons": [[30, "Personal mobile number hai — koi bhi khud ko bank adhikari / police / customer-care bata sakta hai. Number asli hona pehchan ka proof NAHI hai"], [0, "Aisi call par OTP, PIN ya app-install bilkul nahi — service ke official app/number se khud call karke verify karo"]], "hard": 0, "kind": "Phone Number"}
    if len(d) >= 7:
        return {"score": 25, "reasons": [[25, "Ye number kisi jaani-pehchani category me nahi aaya — caller ko official channel se verify karo"]], "hard": 0, "kind": "Phone Number"}
    return {"score": 20, "reasons": [[20, "Number samajh nahi aaya"]], "hard": 0, "kind": "Phone Number"}


def scan(raw):
    text = (raw or "").strip()
    if not text:
        return None
    if re.match(r"^(data|javascript|blob|file):", text, re.I):
        u = score_url(text, False)
        return {"score": u["score"], "reasons": u["reasons"], "hard": u["hard"], "kind": "Link", "official": u["official"]}
    url_match = [m.group(0) for m in URL_RE.finditer(text)]
    vpa_match = [m.group(0) for m in VPA_RE.finditer(text)]
    is_single = len(text.split()) <= 3 and not re.search(r"[.!?]\s", text)
    digits = re.sub(r"[^0-9]", "", text)
    if re.fullmatch(r"\+?[\d\s\-()]{7,16}", text, A) and 7 <= len(digits) <= 13:
        return score_phone(text)
    if is_single and vpa_match and vpa_match[0] == text:
        v = score_vpa(text)
        return {"score": v["score"], "reasons": v["reasons"], "hard": v["hard"], "kind": "UPI ID"}
    if is_single and url_match:
        u = score_url(text, False)
        return {"score": u["score"], "reasons": u["reasons"], "hard": u["hard"], "kind": "Link", "official": u["official"]}
    msg = score_message(text)
    best = {"score": msg["score"], "reasons": list(msg["reasons"]), "hard": msg["hard"], "kind": "Message"}
    if url_match:
        for um in url_match:
            u = score_url(um, True)
            combined = msg["score"] + u["score"] - (u["score"] if u["official"] else 0)
            sc = max(85, combined) if u["hard"] else max(u["score"], min(combined, 100))
            if sc >= best["score"]:
                best = {"score": sc, "reasons": list(msg["reasons"]) + list(u["reasons"]), "hard": u["hard"] or msg["hard"], "kind": "Message + Link"}
    if vpa_match:
        for vm in vpa_match:
            if "." in vm:
                continue
            v = score_vpa(vm)
            if v["hard"]:
                best = {"score": max(85, best["score"]), "reasons": list(best["reasons"]) + list(v["reasons"]), "hard": 1, "kind": best["kind"]}
            elif v["score"] > 0 and best["score"] < 35:
                best["reasons"] = list(best["reasons"]) + list(v["reasons"])
    lt = text.lower()
    if url_match and ("parcel" in lt or "delivery" in lt or "track" in lt) and 0 < best["score"] < 55 and not msg["hard"]:
        best["reasons"].append([5, "Delivery/tracking wala message — courier ka official app hi use karo"])
    best["score"] = min(max(best["score"], 85 if msg["hard"] else 0), 100)
    return best


def analyze_all(text):
    items = []
    seen = set()
    url_match = [m.group(0) for m in URL_RE.finditer(text)]
    for um in url_match:
        if um in seen:
            continue
        seen.add(um)
        u = score_url(um, len(url_match) > 0 and text.strip() != um)
        items.append({"label": um, "score": u["score"], "host": u["host"], "official": u["official"]})
    vpa_match = [m.group(0) for m in VPA_RE.finditer(text)]
    for vm in vpa_match:
        if "." in vm or vm in seen:
            continue
        seen.add(vm)
        v = score_vpa(vm)
        items.append({"label": vm, "score": v["score"]})
    return items


def band(s):
    if s >= 85:
        return {"label": "🔴 DANGER — Ruk jao, tap mat karo", "css": "dan", "guidance": "Ye scam hone ke pakke sanket mile. Paisa/OTP bilkul mat do. 1930 par call karo ya cybercrime.gov.in par report karo."}
    if s >= 55:
        return {"label": "🟠 HIGH RISK — Lagbhag pakka scam hai", "css": "high", "guidance": "Aage mat badho. Service ko uske official app se khud kholo."}
    if s >= 25:
        return {"label": "🟡 CAUTION — Verify nahi ho paya", "css": "cau", "guidance": "Hum ise verify nahi kar paye. Password, OTP ya payment tab tak mat karo jab tak official app/website se khud na pahuncho."}
    return {"label": "🟢 LOW RISK — Koi strong scam signal nahi mila", "css": "low", "guidance": "Iska matlab guarantee NAHI hai. Address khud ek baar padh kar hi aage badho — OTP/PIN kabhi share nahi hota."}


def extract_domain(text):
    """Pehle URL se registrable domain nikalo (RDAP ke liye). IP host par None."""
    m = URL_RE.search(text or "")
    if not m:
        return None
    u = score_url(m.group(0), False)
    host = u.get("host") or ""
    if not host or re.fullmatch(r"[0-9.]+", host):
        return None
    return {"host": host, "registrable": registrable(host), "official": bool(u.get("official"))}
