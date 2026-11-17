# Suraksha Setu — AI Scam Shield

**Tap karne se pehle check karo.** Paste a link, UPI ID, phone number or message — or scan a QR photo — and get a **0–100 risk score with plain-language reasons in Hinglish**, before you tap, pay or reply.

🔴 **Live demo:** https://adityasunny06help-coder.github.io/suraksha-setu-prototype/
📦 **Repository:** https://github.com/adityasunny06help-coder/suraksha-setu-prototype

*PRASUNEX INNOVATHON 2026 — Team Aditya (Aditay Kumar). The engine is an on-device heuristic risk engine — no cloud AI, no data leaves the device. ("AI" is part of the registered project name; no trained ML model runs in this build.)*

---

## What's new in v3.1 (live demo update)

- The demo page now states the honest descriptor on its own screen: on-device heuristic risk engine — no cloud AI, no data leaves the device.
- Added one sourced context line: I4C/NCRP 2025 — 24,02,579 complaints, ₹22,495 crore reported by citizens (Source: PIB; this is the citizens' reported amount, not a bank-loss total).
- Self-audit fixes: scan history and per-item results now render user input as inert text (stored-XSS fix); the whitelist gate now returns before any other rule, so official domains never show contradictory danger reasons; email addresses are no longer misread as UPI IDs; the Hindi toggle now switches the full static UI, not just the result panel; the copy-report button no longer claims success when the clipboard write fails.
- All 6 built-in sample scores are unchanged (85 / 0 / 85 / 85 / 30 / 0) — regression-verified before and after the update.

---

## Try these 5 sample inputs

Copy-paste any of these into the live demo and press **Scan Karo**:

```
https://sbi-kyc-verify.top/login
```
→ **85 · DANGER** — "sbi" in the host, but not an official SBI domain (brand impersonation)

```
https://www.sbi.bank.in
```
→ **0 · LOW RISK** — official domain match (the safe control: genuine links are not falsely flagged)

```
https://meesho-offer-free.vercel.app/login
```
→ **85 · DANGER** — brand login page on free hosting

```
I am CBI officer. A parcel with drugs in your name is seized. You are under digital arrest. Stay on WhatsApp video call, tell no one, transfer money to RBI verification account.
```
→ **85 · DANGER** — Digital Arrest hard pattern (officer + video call + secrecy + transfer)

```
9876543210
```
→ **30 · CAUTION** — a personal mobile number; a real number is not proof of a real officer

---

## How scoring works

```
Input ─► Classifier ─► Specialist scorers ─► Whitelist gate ─► 0–100 score + reasons
         (Link / UPI /    scoreURL()           isOfficial()
          Phone /         scoreVPA()            ├─ official → capped LOW RISK
          Message / QR)   scoreMessage()        └─ not official → hard rules + signals
                          scorePhone()
```

1. **Whitelist-first.** A built-in registry of ~30 official brands/services (SBI, HDFC, PNB, Paytm, IRCTC, UIDAI, …) is checked *before* any risk scoring — genuine links are never falsely flagged.
2. **Never false-safe.** Anything unrecognised scores at least CAUTION — never "safe". Even LOW RISK is shown with a "not a guarantee" note.
3. **Hard rules force DANGER (≥85):** brand impersonation, typosquat within Levenshtein distance 1–2 of a brand, brand page on free hosting / raw IP, punycode + sensitive page, direct APK/EXE download, Digital Arrest pattern, PIN-to-receive, fee-to-withdraw, sextortion.
4. **Additive signals build the rest,** each with a named, user-visible reason: unrecognised domain +15, raw IP +35, URL shortener +20, free hosting +20, risky TLD +18, OTP ask +25, urgency +10, secrecy +10, and more.
5. **Explainable output:** verdict band (DANGER ≥85 · HIGH RISK ≥55 · CAUTION ≥25 · LOW RISK <25), a reason list with point values, 4 category sub-scores (Identity · Link Structure · Message Pattern · Payment/UPI), and domain anatomy (subdomain / real domain / TLD / official status).

## Privacy — and how to verify it yourself

- **100% on-device.** One HTML file, zero dependencies, no backend, no accounts, no analytics, no network calls. The message being checked never leaves the device; the only stored data is the last-5 scan history in your own browser (`localStorage`).
- **Verify:** turn on **airplane mode** and open the live demo (or the downloaded `index.html`) — every check still works offline.

## Implemented (live today, v3.1)

- One input for 5 input types: **link · UPI ID · phone number · full message · QR photo** (BarcodeDetector)
- Link engine: impersonation, typosquat, punycode/homograph, free-hosting & tunnel domains, shorteners, risky TLDs, raw-IP hosts, `@`-trick URLs, dangerous schemes, APK/EXE downloads
- UPI checker: lookalike handles, brand/lure names, unknown handle = "payee not verified", PIN-to-receive myth-bust
- Message engine: Digital Arrest, KYC-expiry, courier/customs, bijli-disconnect, challan, loan-fee, task/job, sextortion + OTP/urgency/secrecy signals
- Phone checker: personal mobile vs 140 / 160 / 1800 series, with honest per-category guidance
- Hinglish UI + full **Hindi UI** toggle · **Elder Mode** (125% text, larger buttons)
- **Hindi voice alert** (SpeechSynthesis) + **voice input** (SpeechRecognition)
- **WhatsApp family alert** (wa.me) with the full report · copyable report · scan history (last 5, on-device)
- **1930 helpline button** on high-risk results + cybercrime.gov.in direction
- 6 built-in demo samples

## Planned (roadmap — NOT built yet)

- On-device ML classifier layered over the rule engine (still fully offline)
- Android app + WhatsApp share-intent
- More Indian languages; larger official-domain / UPI-handle registries
- Opt-in, anonymised community reporting feed (the only planned server component)
- Deeper 1930 / cybercrime.gov.in reporting hand-off

## Limitations

- **Heuristic engine, not a guarantee** — the app says so on its own screen. LOW RISK means no strong scam signal was found; never share OTP/PIN regardless of any score.
- **Finite whitelist (~30 brands):** a genuine smaller bank/company not yet listed scores CAUTION by design, not LOW RISK.
- **New scam phrasing can evade message patterns** — the planned ML layer targets this.
- **QR scan needs `BarcodeDetector`** (Chrome/Android); **voice input needs `SpeechRecognition`** (Chrome-family). Both degrade gracefully with a clear fallback message.
- **Web MVP, not a native app** — no Android app, backend or ML model exists in the current build.

## Run it locally

No build, no install:

1. Open `index.html` in any browser, **or**
2. `python3 -m http.server 8000` in this folder → http://localhost:8000

## Testing

- v2 engine: 32 curated cases, **32/32 PASS** (project build log, 13 Nov 2026)
- v3 engine: **41/41 local PASS**, **3/3 live PASS** on the deployed build (CodeQuest Final Build documentation, §7)
- The 6 built-in samples above are reproducible on the live demo — no accuracy % is claimed; these are curated functional tests, not a field evaluation.

## Team

**Team Aditya — Aditay Kumar** (solo team). Built for PRASUNEX INNOVATHON 2026 with AI-assisted development, disclosed per the event rules. No third-party code libraries or external APIs are used.

*Scam lage to 1930 par call karo ya cybercrime.gov.in par report karo.*
