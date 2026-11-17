// Suraksha Setu v4 — i18n: Hindi/Hinglish dictionary + language state + static UI apply.
// Dictionary v3.1 se verbatim (honest line v4 architecture ke hisaab se update — dekho AUDIT-V4.md).
import { renderHist } from './history.js';
export const T = {hing:{danger:"🔴 DANGER — Ruk jao, tap mat karo",high:"🟠 HIGH RISK — Lagbhag pakka scam hai",cau:"🟡 CAUTION — Verify nahi ho paya",low:"🟢 LOW RISK — Koi strong scam signal nahi mila",
gd:"Ye scam hone ke pakke sanket mile. Paisa/OTP bilkul mat do. 1930 par call karo ya cybercrime.gov.in par report karo.",gh:"Aage mat badho. Service ko uske official app se khud kholo.",gc:"Password, OTP ya payment tab tak mat karo jab tak official app/website se khud na pahuncho.",gl:"Iska matlab guarantee NAHI hai. Address khud padh kar hi aage badho — OTP/PIN kabhi share nahi hota.",reasons:"Kaaran (reasons)",items:"Har cheez ka alag score",anatomy:"Domain ki asaliyat",
tagline:'Link, UPI ID, phone number, message ya QR — <b>tap karne se pehle</b> check karo. Pehle official-domain whitelist se verify hota hai; pehchana nahi gaya to "safe" kabhi nahi bolta.',
honest:"Sach ye hai: ye koi cloud AI nahi hai — ye ek on-device heuristic risk engine hai. Saari jaanch tumhare phone/browser me hi hoti hai. Agar project ka apna backend juda ho to sirf domain ki umar (RDAP) jaanchne ke liye wahi domain usi backend ko bheja jata hai — tumhara paste kiya hua text kahin store NAHI hota.",
stat:"📊 Kyun zaroori hai: I4C/NCRP ke hisaab se 2025 me 24,02,579 cyber-fraud complaints aayi aur citizens ne ₹22,495 crore ka nuksan report kiya (Source: PIB). Ye citizens dwara report kiya gaya amount hai — koi bank-loss ka kul aankda nahi.",
ph:"Link / UPI ID / phone number / message paste karo",scan:"🔍 Scan Karo",voice:"🔊 Voice Alert",voicein:"🎤 Bolkar Batao",elder:"👴 Bade Akshar (Elder Mode)",qr:"📷 QR Photo Scan",samples:"Samples:",
demos:["Scam KYC link","Asli SBI","Meesho nakli offer","Digital Arrest msg","Personal number se officer","Asli PNB"],
note:"Note: Ye tool guarantee nahi deta. OTP/PIN kabhi share mat karo. Scam lage to 1930 par call karo ya cybercrime.gov.in par report karo. QR scan Chrome/Android par chalta hai.",
hist:"🕘 Pichhle scans:",empty:"Pehle kuch paste karo.",catH:"📊 Category score:",nopat:"Koi khaas pattern nahi mila",
sub:"Subdomain:",reald:"Asli domain:",offYes:"✅ <b>Official whitelist me hai</b>",offNo:"⚠️ Official list me NAHI hai",
copy:"📋 Report Copy Karo",wa:"📲 Family ko WhatsApp Alert",call1930:"📞 1930 par Call Karo",
copied:"Report copy ho gaya",copyfail:"Copy nahi ho paya — report ko khud select karke copy karo",
scanFirst:"Pehle Scan karo",noVoiceIn:"Is browser me voice input nahi hai",
qrNo:"⚠️ Is browser me QR scan supported nahi hai — QR wala link/UPI type karke dalo.",qrFail:"QR code padh nahi paya — saaf photo try karo.",qrErr:"QR scan me dikkat aayi — link type karke dalo.",
alertsH:"📰 Live Scam Alerts (sarkari/news sources se)",ageH:"🌐 Domain Age (RDAP live check)",ageReg:"Registered:",ageDays:"din purana",ageNotFound:"RDAP me is domain ka koi registration record NAHI mila — ye khud ek bada red flag hai",staleTag:"(purana cache — source abhi unreachable hai)"},
hindi:{danger:"🔴 खतरा — रुक जाओ, टैप मत करो",high:"🟠 उच्च जोखिम — लगभग पक्का घोटाला है",cau:"🟡 सावधान — सत्यापित नहीं हो पाया",low:"🟢 कम जोखिम — कोई मजबूत घोटाले का संकेत नहीं मिला",
gd:"यह घोटाला होने के पक्के संकेत मिले। पैसा/OTP बिल्कुल मत दो। 1930 पर कॉल करो या cybercrime.gov.in पर रिपोर्ट करो।",gh:"आगे मत बढ़ो। सेवा को उसके आधिकारिक ऐप से खुद खोलो।",gc:"पासवर्ड, OTP या भुगतान तब तक मत करो जब तक आधिकारिक ऐप/वेबसाइट से खुद न पहुँचो।",gl:"इसका मतलब गारंटी नहीं है। पता खुद पढ़कर ही आगे बढ़ो — OTP/PIN कभी साझा नहीं होता।",reasons:"कारण",items:"हर चीज़ का अलग स्कोर",anatomy:"डोमेन की असलियत",
tagline:'लिंक, UPI ID, फ़ोन नंबर, संदेश या QR — <b>टैप करने से पहले</b> जाँचो। पहले आधिकारिक-डोमेन व्हाइटलिस्ट से सत्यापन होता है; पहचाना नहीं गया तो "सुरक्षित" कभी नहीं बोलता।',
honest:"सच यह है: यह कोई cloud AI नहीं है — यह एक on-device heuristic risk engine है। सारी जाँच तुम्हारे फ़ोन/browser में ही होती है। अगर project का अपना backend जुड़ा हो तो सिर्फ़ domain की उम्र (RDAP) जाँचने के लिए वही domain उसी backend को भेजा जाता है — तुम्हारा paste किया हुआ text कहीं store नहीं होता।",
stat:"📊 क्यों ज़रूरी है: I4C/NCRP के अनुसार 2025 में 24,02,579 साइबर-धोखाधड़ी शिकायतें आईं और नागरिकों ने ₹22,495 करोड़ का नुकसान report किया (स्रोत: PIB)। यह नागरिकों द्वारा report किया गया amount है — कोई bank-loss का कुल आँकड़ा नहीं।",
ph:"लिंक / UPI ID / फ़ोन नंबर / संदेश यहाँ डालो",scan:"🔍 स्कैन करो",voice:"🔊 आवाज़ चेतावनी",voicein:"🎤 बोलकर बताओ",elder:"👴 बड़े अक्षर (Elder Mode)",qr:"📷 QR फ़ोटो स्कैन",samples:"उदाहरण:",
demos:["घोटाला KYC लिंक","असली SBI","Meesho नकली ऑफ़र","डिजिटल अरेस्ट संदेश","निजी नंबर से अधिकारी","असली PNB"],
note:"नोट: यह टूल गारंटी नहीं देता। OTP/PIN कभी साझा मत करो। घोटाला लगे तो 1930 पर कॉल करो या cybercrime.gov.in पर रिपोर्ट करो। QR स्कैन Chrome/Android पर चलता है।",
hist:"🕘 पिछले स्कैन:",empty:"पहले कुछ डालो।",catH:"📊 श्रेणी स्कोर:",nopat:"कोई खास पैटर्न नहीं मिला",
sub:"सबडोमेन:",reald:"असली डोमेन:",offYes:"✅ <b>आधिकारिक व्हाइटलिस्ट में है</b>",offNo:"⚠️ आधिकारिक सूची में नहीं है",
copy:"📋 रिपोर्ट कॉपी करो",wa:"📲 परिवार को WhatsApp अलर्ट",call1930:"📞 1930 पर कॉल करो",
copied:"रिपोर्ट कॉपी हो गया",copyfail:"कॉपी नहीं हो पाया — रिपोर्ट को खुद चुनकर कॉपी करो",
scanFirst:"पहले स्कैन करो",noVoiceIn:"इस browser में voice input नहीं है",
qrNo:"⚠️ इस browser में QR स्कैन समर्थित नहीं है — QR वाला लिंक/UPI टाइप करके डालो।",qrFail:"QR code पढ़ नहीं पाया — साफ़ फ़ोटो try करो।",qrErr:"QR स्कैन में दिक्कत आई — लिंक टाइप करके डालो।",
alertsH:"📰 लाइव घोटाला अलर्ट (सरकारी/समाचार स्रोतों से)",ageH:"🌐 डोमेन आयु (RDAP लाइव जाँच)",ageReg:"पंजीकृत:",ageDays:"दिन पुराना",ageNotFound:"RDAP में इस डोमेन का कोई पंजीकरण रिकॉर्ड नहीं मिला — यह खुद एक बड़ा ख़तरे का संकेत है",staleTag:"(पुराना cache — स्रोत अभी उपलब्ध नहीं है)"}};
let LANG = 'hing';
export function getLang(){ return LANG; }
export function getT(){ return T[LANG]; }
export function setLang(l){ LANG = l; applyLang(); }
export function applyLang(){
  const t = T[LANG];
  const S = (id, txt)=>{ const e=document.getElementById(id); if(e) e.textContent = txt; };
  const tg = document.getElementById('tagline'); if(tg) tg.innerHTML = t.tagline;
  const inpEl = document.getElementById('inp'); if(inpEl) inpEl.placeholder = t.ph;
  const hn = document.getElementById('honestLine'); if(hn) hn.textContent = t.honest;
  const st = document.getElementById('statLine'); if(st) st.textContent = t.stat;
  S('scanBtn', t.scan); S('voiceBtn', t.voice); S('voiceInBtn', t.voicein); S('elderBtn', t.elder);
  S('qrLbl', t.qr); S('samplesH', t.samples); S('noteLine', t.note);
  t.demos.forEach((d,i)=>S('demo'+i, d));
  renderHist();
}
