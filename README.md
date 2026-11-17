# 🛡️ Suraksha Setu — AI Scam Shield (v4, Advanced Polyglot)

**Live demo (poora app — frontend + backend):** https://suraksha-setu-prototype.vercel.app/
**Backup demo (sirf frontend, standalone mode):** https://adityasunny06help-coder.github.io/suraksha-setu-prototype/
**Repo:** https://github.com/adityasunny06help-coder/suraksha-setu-prototype

Link, UPI ID, phone number, message ya QR photo — **tap karne se pehle** scam check karo.
Pehle official-domain whitelist se verify hota hai; jo pehchana na jaye use "safe" kabhi nahi bola jata.

> **Sach ye hai:** ye koi cloud AI nahi hai — ye ek **on-device heuristic risk engine** hai.
> Saari jaanch tumhare phone/browser me hi hoti hai. Agar project ka apna backend juda ho to
> sirf domain ki umar (RDAP) jaanchne ke liye wahi domain usi backend ko bheja jata hai —
> **tumhara paste kiya hua text kahin store NAHI hota** (backend sirf anonymous daily counters rakhta hai).

📊 **Kyun zaroori hai:** I4C/NCRP ke hisaab se 2025 me 24,02,579 cyber-fraud complaints aayi aur citizens ne
₹22,495 crore ka nuksan report kiya (Source: PIB). Ye citizens dwara report kiya gaya amount hai —
koi bank-loss ka kul aankda nahi.

---

## v4 me kya badla — Advanced Polyglot Rebuild

v3.1 tak Suraksha Setu ek single-file HTML app tha. **v4 me poori architecture badli hai:**
frontend kai JS modules me, backend Python (FastAPI) me, data SQLite/SQL me,
aur backend ke paas ek asal **LIVE signal** hai — RDAP se domain ki umar.
Detector ke saare rules aur scores v3.1 se **bilkul barkarar** hain
(regression gate: 6 built-in samples = 85/0/85/85/30/0, dono languages me).

### Architecture

```
            ┌────────────────────────── FRONTEND (static, koi framework nahi) ─┐
 Browser ──▶│ index.html + style.css + js/ modules                             │
            │  engine.js  detector (whitelist-first, brand/typosquat, patterns)│
            │  ui.js      rendering (esc/textContent discipline)               │
            │  i18n.js    Hindi/Hinglish — pura UI switch                      │
            │  voice.js   Hindi voice alert + voice input                      │
            │  qr.js      QR photo scan (BarcodeDetector)                      │
            │  history.js localStorage scan history (XSS-safe)                 │
            │  alerts.js  backend jod (optional, fail-silent)                  │
            │  app.js     sab ki wiring                                        │
            └──────────────┬───────────────────────────────────────────────────┘
                           │  sirf tab, jab backend reachable ho:
                           │  POST /api/check (domain-age ke liye) · GET /api/alerts
            ┌──────────────▼────────────── BACKEND (Python + FastAPI) ─────────┐
            │ backend/main.py    API endpoints + CORS (dev localhost)          │
            │ backend/engine.py  detector ka Python port (parity-tested)       │
            │ backend/rdap.py    RDAP domain-age (rdap.org + Verisign fallback)│
            │ backend/alerts.py  live RSS headlines + SQLite cache (stale-safe)│
            │ backend/db.py      SQLite (SS_DB_PATH, /tmp fallback, no-crash)  │
            │ backend/schema.sql counters + caches (user text KABHI nahi)      │
            │ api/index.py       Vercel serverless entrypoint (wahi app)       │
            └──────────────────────────────────────────────────────────────────┘
```

### Languages — har ek ka asli kaam

| Language | Kahan | Kya kaam |
|---|---|---|
| HTML | `index.html` | Page structure (sirf structure + links) |
| CSS | `style.css` | Poori styling, Elder Mode bade akshar |
| JavaScript | `js/*.js` (8 modules) | On-device detector, UI, voice, QR, history, backend jod |
| Python | `backend/*.py` | FastAPI service, detector port, RDAP + RSS live data |
| SQL | `backend/schema.sql` | Counters, alerts cache, RDAP cache, feed status |
| Bash | `run.sh`, `test.sh` | Dev server jodi + poora test suite ek command me |
| JSON | `vercel.json` | Vercel routing (`/api/*` → serverless function) |

---

## Features

- **Ek input, sab check:** Link / UPI ID / Phone number / Message / QR photo
- **Whitelist-first engine:** official domain sabse pehle match — pehchana nahi gaya to "safe" nahi bolta
- **0–100 risk score** + 4 category sub-scores (Pehchan, Link Banawat, Message Pattern, Payment/UPI)
- **Domain ki asaliyat:** subdomain / asli domain / TLD / official hai ya nahi
- **Brand impersonation + typosquat** jaanch (Levenshtein), punycode/homograph, free-hosting, IP-host — hard rules
- **Message patterns:** Digital Arrest, KYC, courier/customs, bijli-disconnect, challan, task/job, loan-fee, sextortion
- **Phone checker:** 140 = telemarketing, 160 = service series, personal number = pehchan ka proof nahi
- **RDAP domain-age (backend, LIVE):** domain kab register hua — naya domain = extra risk signal; record hi na mile to woh bhi red flag
- **Live scam alerts (backend):** PIB + Google News RSS se headlines, source + fetched-at ke saath, purana cache `stale` label ke saath
- **Hinglish + Hindi UI** (pura UI switch hota hai), **Elder Mode**, **Hindi voice alert + voice input**
- **Family WhatsApp alert** + Danger par **1930 call** button, scan history

## Backend API

| Endpoint | Kaam |
|---|---|
| `GET /api/health` | Liveness — `{status:"ok", version:"4.0"}` |
| `POST /api/check` `{input}` | Python engine ka score/band/reasons + domain + **RDAP domain-age** (found/registered_on/age_days/risk_points). Input 1–4000 chars validate hota hai. User ka URL server se **kabhi fetch nahi** hota (SSRF discipline) — sirf domain ka RDAP record dekha jata hai |
| `GET /api/alerts` | Live headlines `{items, fetched_at, stale}` — 30 min cache, feed fail ho to purana cache stale label ke saath |

**Privacy:** scan ka text database me kabhi store nahi hota. DB me sirf hai:
anonymous daily counters (date, total_scans, danger_count), public RSS headlines ka cache,
aur public domains ke RDAP results ka cache. (Test se proven: unique marker text DB file me nahi milta.)

## Local me chalana

```bash
./run.sh        # backend :8000 + frontend :8080 ek saath (pehli baar venv + deps automatic)
# ya alag-alag:
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/uvicorn main:app --port 8000
python3 -m http.server 8080                               # repo root se (dusre terminal me)
```

Frontend **bina backend ke bhi 100% chalta hai** — backend mile to domain-age line aur
alerts strip apne aap jud jati hai, na mile to chup-chaap standalone.
API base ka order: `window.SS_API_BASE` → `?api=` URL param → same-origin `/api` → `http://localhost:8000`.

## Tests

```bash
./test.sh
```

- **Backend (pytest, 26 tests):** cross-language parity (Python me bhi 6/6 scores),
  **84-case deep-review battery** (typosquat/@-trick/IP/shortener/UPI/phone/message patterns + benign FP guards),
  RDAP parse/fallback/404 + exception-degrade, RSS parse + per-feed isolation, API validation,
  privacy (user text DB me nahi), Vercel entrypoint import smoke
- **Frontend (node --test, 12 tests):** regression gate 6/6, wahi 84-case battery JS engine par,
  i18n key parity, esc/XSS discipline (incl. attribute-breakout payloads), jsdom DOM tests (history stored-XSS fix, pura language switch)

## Deploy

- **GitHub Pages:** repo root ka static frontend serve hota hai — backend wala hissa
  Pages par nahi chalta (wahan demo hamesha standalone mode me rehta hai).
- **Vercel (poora app, frontend + backend ek domain par): LIVE hai** —
  https://suraksha-setu-prototype.vercel.app (18 Nov 2026 ko deploy + live verify:
  /api/health ok, /api/check par scam link 85 + official 0 with RDAP age, /api/alerts live items).
  Dobara deploy karna ho to:
  1. GitHub par ye repo push karo (Vercel GitHub se juda hai — naye commit par khud redeploy hota hai)
  2. Vercel me repo **Import** karo (koi framework preset nahi — "Other")
  3. Deploy — `api/index.py` serverless function ban jayega, root `requirements.txt`
     (fastapi + httpx) install hoga, `vercel.json` `/api/*` ko function par bhejega
  4. Env vars: **koi secret nahi chahiye.** Optional: `SS_DB_PATH=/tmp/suraksha-setu.db`
     (default bhi /tmp fallback khud kar leta hai)
  - ⚠️ Serverless par SQLite **ephemeral** hai — counters/cache garam instance tak
    rehte hain, cold start par reset ho sakte hain. Kal ko asal persistence chahiye
    to external DB lagega; abhi ke liye ye seema jaan-boojh kar sweekar ki gayi hai.

## Seemayein (imaandari se)

- Heuristic engine hai — guarantee nahi deta. OTP/PIN kabhi share mat karo; scam lage to **1930** par call karo ya cybercrime.gov.in par report karo.
- RDAP sab TLDs par ek jaisa nahi milta; lookup fail ho to domain-age signal bas gayab rehta hai, galat data nahi banta.
- CERT-In aur RBI ke public RSS endpoints is samay asal RSS nahi dete (verify kiya gaya) — isliye alerts PIB + Google News se aate hain, har item par source likha hota hai.
- QR scan Chrome/Android (BarcodeDetector) par chalta hai.

## Version itihaas

- **v2** — whitelist-first engine · **v3** — QR, phone checker, Hindi/Elder mode, WhatsApp alert
- **v3.1** — honest descriptor, sourced stat, 7 audit fixes (incl. stored-XSS)
- **v4** — advanced polyglot rebuild: modular JS frontend + Python FastAPI backend + SQLite + live RDAP/RSS (ye version)
- **v4.1** — final deep-review (FINAL-AUDIT.md): 84-case battery par 11 detector fixes (dangerous-scheme routing, brand coverage PayPal/WhatsApp/Microsoft/Netflix/Instagram/Telegram, lure-UPI floor, task-scam/collect-request naye patterns, "aapke"→apk aur "kabhi"→abhi substring FP fixes), RDAP exception par 500-degrade fix, i18n/a11y gaps (table headers, WhatsApp text, focus outline, aria-label)
- Aage ka roadmap (Flutter/FastAPI/TFLite wala purana plan) **future plan hai, bana hua nahi** — jab banega tabhi yahan likhega.
