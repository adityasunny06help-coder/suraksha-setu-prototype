// Suraksha Setu v4 — scan history (localStorage).
// XSS discipline (v3.1 ka sabse gambheer fix, barkarar): history hamesha
// createElement + textContent se banti hai — user input kabhi innerHTML nahi banta.
import { getT } from './i18n.js';

const KEY = 'ss_hist';
let pickHandler = null;

export function setHistPickHandler(fn){ pickHandler = fn; }

export function saveHist(q, s){
  try{
    let h = JSON.parse(localStorage.getItem(KEY) || '[]');
    h.unshift({ q: q.slice(0, 45), s });
    h = h.slice(0, 5);
    localStorage.setItem(KEY, JSON.stringify(h));
    renderHist();
  }catch(e){}
}

export function renderHist(){
  try{
    const h = JSON.parse(localStorage.getItem(KEY) || '[]');
    const box = document.getElementById('histBox');
    if(!box) return;
    box.innerHTML = '';
    if(!h.length) return;
    const hd = document.createElement('h3');
    hd.textContent = getT().hist;
    box.appendChild(hd);
    for(const x of h){
      const sp = document.createElement('span');
      sp.className = 'chip hist';
      sp.textContent = String(x.q) + '… — ';
      const b = document.createElement('b');
      b.textContent = x.s + '/100';
      sp.appendChild(b);
      sp.addEventListener('click', ()=>{ if(pickHandler) pickHandler(x.q); });
      box.appendChild(sp);
    }
  }catch(e){}
}
