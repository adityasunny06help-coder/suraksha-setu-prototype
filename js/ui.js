// Suraksha Setu v4 — UI rendering helpers.
// Rendering safety: jo HTML string banta hai usme user-controlled har value
// esc() se guzarti hai (v3.1 fix barkarar); baaki strings sirf apne static dictionary se aati hain.
import { registrable, isOfficial, analyzeAll } from './engine.js';
import { getT } from './i18n.js';

export function esc(s){
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

export function nrm(r){ return Array.isArray(r) ? r : [0, r]; }

export function bandText(s){
  const t = getT();
  return s >= 85 ? [t.danger, 'dan', t.gd]
       : s >= 55 ? [t.high, 'high', t.gh]
       : s >= 25 ? [t.cau, 'cau', t.gc]
       : [t.low, 'low', t.gl];
}

export function cats(reasons){
  const c = {'Pehchan (Identity)':0, 'Link Banawat':0, 'Message Pattern':0, 'Payment/UPI':0};
  for(const r0 of reasons){
    const [p, txt] = nrm(r0);
    const t = (txt || '').toLowerCase();
    if(/brand|impersonation|official|typosquat|puny|homograph|@|ip address|handle/.test(t)) c['Pehchan (Identity)'] += p;
    else if(/lamba|subdomain|hyphen|digit|tld|port|http|shorten|free-hosting|domain pehchana|regist/.test(t)) c['Link Banawat'] += p;
    else if(/upi|pin|collect|fee|payment|sensitive/.test(t)) c['Payment/UPI'] += p;
    else c['Message Pattern'] += p;
  }
  for(const k in c) c[k] = Math.min(c[k], 100);
  return c;
}

export function anatomy(raw){
  try{
    const u = new URL(/^https?:\/\//i.test(raw) ? raw : 'https://' + raw);
    const host = u.hostname;
    const reg = registrable(host);
    const sub = host === reg ? '—' : host.slice(0, host.length - reg.length - 1);
    const tld = host.split('.').pop();
    const off = isOfficial(host);
    return { sub, reg, tld, off };
  }catch(e){ return null; }
}

export function buildResultHTML(r, v){
  const t = getT();
  const b = bandText(r.score);
  const col = r.score >= 85 ? '#f87171' : r.score >= 55 ? '#fb923c' : r.score >= 25 ? '#facc15' : '#4ade80';
  let h = '<div class="meter"><div class="fill" style="width:' + r.score + '%;background:' + col + '"></div></div>'
        + '<p class="score ' + b[1] + '">' + r.score + '/100</p><h2 class="' + b[1] + '">' + b[0] + '</h2><p>' + b[2] + '</p>';
  const c = cats(r.reasons);
  h += '<h3>' + t.catH + '</h3>' + Object.keys(c).map(k =>
    '<div class="row"><span>' + k + '</span><div class="mini"><div class="fill" style="width:' + c[k] + '%;background:' + col + ';height:100%"></div></div><b>' + c[k] + '</b></div>').join('');
  const items = analyzeAll(v);
  if(items.length > 1){
    h += '<h3>🔎 ' + t.items + ':</h3><table><tr><th>Cheez</th><th>Score</th></tr>'
       + items.map(i => '<tr><td>' + esc(i.label) + (i.official ? ' ✅ official' : '') + '</td><td><b>' + i.score + '/100</b></td></tr>').join('') + '</table>';
  }
  const first = (v.match(/((https?:\/\/|www\.)[^\s]+|[\w\-]+(\.[\w\-]+)+\.[a-z]{2,}(\/[^\s]*)?)/i) || [])[0];
  if(first){
    const a = anatomy(first);
    if(a) h += '<h3>🧬 ' + t.anatomy + ':</h3><p>' + t.sub + ' <span class="chip">' + esc(a.sub) + '</span> '
             + t.reald + ' <span class="chip"><b>' + esc(a.reg) + '</b></span> TLD: <span class="chip">.' + esc(a.tld) + '</span> '
             + (a.off ? t.offYes : t.offNo) + '</p>';
  }
  h += '<h3>' + t.reasons + ':</h3><ul>'
     + (r.reasons.length
         ? r.reasons.slice(0, 7).map(x => { const [p, txt] = nrm(x); return '<li><b>+' + p + '</b> — ' + esc(txt) + '</li>'; }).join('')
         : '<li>' + t.nopat + '</li>')
     + '</ul>';
  h += '<div><button onclick="copyReport()">' + t.copy + '</button><button class="purple" onclick="waAlert()">' + t.wa + '</button>'
     + (r.score >= 55 ? '<a href="tel:1930"><button style="background:#dc2626">' + t.call1930 + '</button></a>' : '') + '</div>';
  return h;
}

export function buildReportText(r, input){
  if(!r) return '';
  const b = bandText(r.score);
  return '🛡️ Suraksha Setu Scan\nInput: ' + String(input).slice(0, 120)
       + '\nScore: ' + r.score + '/100 — ' + b[0]
       + '\nReasons: ' + r.reasons.slice(0, 3).map(x => nrm(x)[1]).join('; ')
       + '\nCheck khud karo: https://adityasunny06help-coder.github.io/suraksha-setu-prototype/';
}
