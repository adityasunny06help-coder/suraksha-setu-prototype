// Suraksha Setu v4 — app wiring: saare modules ko jodta hai.
// Inline onclick handlers ke liye zaroori functions window par rakhe hain.
import { scan, SAMPLES } from './engine.js';
import { setLang, applyLang, getT } from './i18n.js';
import { bandText, nrm, buildResultHTML, buildReportText } from './ui.js';
import { saveHist, setHistPickHandler } from './history.js';
import { speakText, startVoiceInput } from './voice.js';
import { scanQRFile } from './qr.js';
import { loadAlerts, enrichDomainAge } from './alerts.js';

let lastText = '', lastResult = null, lastInput = '';
const $ = id => document.getElementById(id);

function run(){
  const v = $('inp').value;
  lastInput = v;
  const ageBox = $('ageBox');
  if(ageBox) ageBox.innerHTML = '';
  const r = scan(v);
  if(!r){ $('out').innerHTML = '<p>' + getT().empty + '</p>'; return; }
  lastResult = r;
  const b = bandText(r.score);
  lastText = b[0] + '. Risk score ' + r.score + ' out of 100. '
           + r.reasons.slice(0, 3).map(x => nrm(x)[1]).join('. ');
  $('out').innerHTML = buildResultHTML(r, v);
  saveHist(v, r.score);
  enrichDomainAge(v); // backend ho to RDAP domain-age line judegi, na ho to kuch nahi hoga
}

function demo(i){ $('inp').value = SAMPLES[i]; run(); }

function copyReport(){
  if(!lastResult){ alert(getT().scanFirst); return; }
  const txt = buildReportText(lastResult, lastInput);
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(txt)
      .then(() => alert(getT().copied))
      .catch(() => alert(getT().copyfail));
  } else {
    alert(getT().copyfail);
  }
}

function waAlert(){
  window.open('https://wa.me/?text=' + encodeURIComponent(
    getT().waMsg + '\n\n'
    + buildReportText(lastResult, lastInput)), '_blank');
}

function speak(){
  if(lastText && speakText(lastText)) return;
  alert(getT().scanFirst);
}

function voiceIn(){
  if(!startVoiceInput(txt => { $('inp').value = txt; run(); })) alert(getT().noVoiceIn);
}

async function qrScan(inp){
  const f = inp.files[0];
  if(!f) return;
  const res = await scanQRFile(f);
  if(res.status === 'ok'){ $('inp').value = res.value; run(); }
  else if(res.status === 'unsupported'){ $('out').innerHTML = '<p>' + getT().qrNo + '</p>'; }
  else if(res.status === 'notfound'){ $('out').innerHTML = '<p>' + getT().qrFail + '</p>'; }
  else if(res.status === 'error'){ $('out').innerHTML = '<p>' + getT().qrErr + '</p>'; }
}

window.run = run;
window.demo = demo;
window.copyReport = copyReport;
window.waAlert = waAlert;
window.speak = speak;
window.voiceIn = voiceIn;
window.qrScan = qrScan;
window.setLang = setLang;

setHistPickHandler(q => { $('inp').value = q; run(); });
applyLang();   // static texts + history render (default Hinglish)
loadAlerts();  // backend ho to live alerts strip; na ho to khaali rahega
