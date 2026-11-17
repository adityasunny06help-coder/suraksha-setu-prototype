# AUDIT-V4 — Suraksha Setu v4 (Advanced Polyglot Rebuild) ka self-audit

User ka hukm: *"advance krne ko kaha tha js, python html sara chiz use krke"* — aur uska loop:
**bana → khud reject kar → seekh → phir bana.** Ye file usi loop ka record hai.
Saare live checks 18 Nov 2026, ~01:04–01:06 IST (UTC 19:34–19:36) ko is sandbox se kiye gaye.

---

## 1. Vercel pattern (deploy-ready structure)

- `api/index.py` — `sys.path` me `backend/` jod kar wahi FastAPI `app` import karta hai jo
  local par uvicorn chalata hai. **Ek hi code, do jagah.**
- Root `requirements.txt` (Vercel ke liye, minimal): `fastapi==0.163.2`, `httpx==0.28.1`.
  Local ke liye `backend/requirements.txt` (uvicorn + pytest samet).
- `vercel.json` — rewrite: `/api/(.*)` → `/api/index.py`. Static frontend Vercel
  default serving se chalega; frontend ka API base same-origin `/api` pehle try karta hai.
- **Local smoke (proof):** pytest ka `test_vercel_entrypoint_imports_and_serves` —
  `api/index.py` ko import karke TestClient se `/api/health` → `{"status":"ok"}` PASS.
- SQLite Vercel par: `SS_DB_PATH` env → default `backend/data/` → `/tmp` fallback →
  woh bhi fail to bina DB ke graceful (alerts fresh fetch, counters skip). README me seema likhi hai.

## 2. Live verification (asal network, koi mock nahi)

### RDAP (domain-age)
| Domain | Raasta | Result |
|---|---|---|
| `sbi.bank.in` | rdap.org → rdap.nixiregistry.in | **200** — registered `2025-08-11`, age **463 din** (backend se live jawab mila) |
| `sbi-kyc-verify.top` | rdap.org → rdap.zdnsgtld.com | **404** — koi registration record nahi → `found:false`, risk_points 20 |
| `google.com` | rdap.org → Verisign redirect | **FAIL** (curl 000 / timeout) — neeche flaw #1 dekho |
| `google.com` | rdap.verisign.com direct (fix ke baad) | **200** — registered `1997-09-15`, age **10,655 din**, source `rdap.verisign.com` |

### RSS feeds (alerts)
| Feed | Status | Note |
|---|---|---|
| PIB `RssMain.aspx?ModId=6&Lang=1&Regid=3` | **200, asal RSS** (20 items) | Aam sarkari feed → cyber keywords se filter; live smoke ke samay matching items **0** (feed_status me `ok=1, item_count=0` — imaandari se record) |
| Google News search RSS (cyber fraud India) | **200, asal RSS** | Live smoke: **29 items** fetch, API ne top 10 diye |
| CERT-In `/Rssfeed.xml`, `/rss.xml` | 200 lekin **HTML homepage** | Asal RSS nahi hai — reject, record kiya |
| RBI `/Rssfeeds/pressreleases.xml` (www + bina www) | **404** | Reject, record kiya |

### Chalti hui service (uvicorn, live smoke)
- `GET /api/health` → `{"status":"ok","version":"4.0"}` ✔
- `POST /api/check` `sbi.bank.in` → score **0**, domain_age live (upar) ✔
- `POST /api/check` `sbi-kyc-verify.top/login` → score **85**, domain_age `found:false` ✔
- `POST /api/check` Digital Arrest message → score **85**, domain `null` (sahi — message me domain nahi) ✔
- `GET /api/alerts` pehli call → 10 items, `stale:false`; **dusri call par fetched_at bilkul wahi** → cache hit ka saboot ✔
- DB counters: us din (IST) `total_scans=3, danger_count=2` — teen checks se exact match ✔
- Frontend static: `/`, `/style.css`, `/js/*.js` sab **200** (python http.server) ✔

## 3. Flaws mile → reject → fix

1. **RDAP .com/.net par fail (environment-real).** rdap.org ka Verisign redirect is network
   se slow/flaky hai — mocks me sab pass tha, live me google.com par `domain_age: null` aaya.
   **Fix:** `rdap.py` me endpoint chain — rdap.org pehle, .com/.net par
   `rdap.verisign.com` direct fallback. 404 par fallback NAHI (registry ka "nahi hai" pakka jawab hai).
   Live re-verify: google.com → 200, 10,655 din. Naya test: `test_domain_age_verisign_fallback`.
   *Seekh (program wali hi): environment-real testing pehle — ek baar phir sahi sabit hua.*
2. **Honest descriptor jhooth ho jata.** v3.1 ki line kehti thi "tumhara data device se
   bahar kahi nahi jata" — v4 me backend enrichment ke liye input project ke apne backend
   ko jata hai, to woh daava ab galat hota. **Fix:** dono languages + static HTML me line
   update — on-device jaanch waisi hi, lekin backend juda ho to sirf domain RDAP ke liye
   bheja jata hai aur **text store nahi hota**, ye saaf likha hai.
3. **Frontend me RDAP source hardcoded.** `alerts.js` har haal me "RDAP (rdap.org)" likhta —
   Verisign fallback ke baad woh jhooth hota. **Fix:** source ab API jawab se aata hai.
4. **copyReport ki aadhi-imaandari.** Bina scan kiye Copy dabane par khaali report
   "copy ho gaya" bol sakti thi. **Fix:** pehle scan na ho to `scanFirst` alert (v3.1 ke
   clipboard-failure fix ke saath aage ka kadam).
5. **Node test runner quirk.** `node --test tests/` (trailing slash) is Node par
   MODULE_NOT_FOUND deta hai. **Fix:** `test.sh` explicit file paths chalata hai.
6. **pip install /tmp par fail.** Sandbox ka /tmp 512M tmpfs hai — pehla venv install
   "No space left" se mara. **Fix:** `run.sh`/`test.sh` TMPDIR ko home cache par rakhte hain.

## 4. Jahan flaw NAHI mila (saaf record)

- **innerHTML audit:** `grep innerHTML js/` — bachi hui jagah sirf (a) static dictionary
  strings (tagline/empty/QR messages), (b) `buildResultHTML` jo har user-value ko `esc()`
  se guzarta hai, (c) `innerHTML=''` clearing (4 jagah). History alerts sab
  createElement/textContent se — jsdom test se proven (payload inert text banta hai).
- **Module todne me koi feature nahi toota:** regression gate 6/6 + DOM tests 3/3 PASS.
- **Backend input validation:** pydantic `min_length=1, max_length=4000` → 422 tests PASS;
  whitespace-only input par saaf Empty jawab, crash nahi.
- **RDAP/RSS failure par degrade:** RDAP fail → `domain_age: null`, score engine ka hi rehta
  hai; ek feed down → doosri chalti hai (test proven); saari feeds down + cache khaali →
  `items: [], stale: true` — nakli headline kabhi nahi banti.
- **CORS:** sirf localhost dev origins; production same-origin hai.
- **Privacy:** unique marker text POST karke DB file me khoja — **nahi mila**; counters badhe.

## 5. Test numbers (khud re-run kiye hue)

- Backend pytest: **24/24 PASS** (parity 5, RDAP 7, alerts 5, API 7)
- Frontend node --test: **10/10 PASS** (unit 7 + jsdom DOM 3)
- Cross-language parity (haath se bhi): 12 cases (6 samples + .apk/email/UPI/140/typosquat-host)
  Python aur JS me **bilkul same scores**
- Live smoke: upar section 2 ki table — sab asal network se

## 6. Deploy ke liye ready files (Vercel)

`api/index.py` · root `requirements.txt` · `vercel.json` · `backend/` (poora) ·
frontend root files (`index.html`, `style.css`, `js/`) — GitHub upload + Vercel import
browser route se hoga (is environment se git push nahi hota). Koi secret repo me nahi hai.
