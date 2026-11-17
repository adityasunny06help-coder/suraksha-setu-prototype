// Suraksha Setu v4 — backend jod (OPTIONAL enrichment).
// Frontend 100% standalone hai: backend na mile to ye module chup rehta hai,
// koi error nahi dikhata, on-device result waise ka waisa rehta hai.
// API base order: window.SS_API_BASE -> ?api= param -> same-origin '' (Vercel par yahi chalega) -> http://localhost:8000 (local dev).
import { getT } from './i18n.js';

let basePromise = null;

function candidates(){
  const list = [];
  if(window.SS_API_BASE) list.push(String(window.SS_API_BASE).replace(/\/$/, ''));
  const q = new URLSearchParams(location.search).get('api');
  if(q) list.push(q.replace(/\/$/, ''));
  list.push('');
  list.push('http://localhost:8000');
  return [...new Set(list)];
}

async function probe(base){
  try{
    const ctl = new AbortController();
    const to = setTimeout(() => ctl.abort(), 2500);
    const r = await fetch(base + '/api/health', { signal: ctl.signal });
    clearTimeout(to);
    if(!r.ok) return false;
    const j = await r.json();
    return !!(j && j.status === 'ok');
  }catch(e){ return false; }
}

export function apiBase(){
  if(!basePromise){
    basePromise = (async () => {
      for(const b of candidates()){
        if(await probe(b)) return b;
      }
      return null;
    })();
  }
  return basePromise;
}

export async function loadAlerts(){
  const base = await apiBase();
  if(base === null) return;
  try{
    const r = await fetch(base + '/api/alerts');
    if(!r.ok) return;
    renderAlerts(await r.json());
  }catch(e){ /* standalone — chup */ }
}

function renderAlerts(j){
  const box = document.getElementById('alertsBox');
  if(!box || !j || !Array.isArray(j.items) || !j.items.length) return;
  const t = getT();
  box.innerHTML = '';
  const h = document.createElement('h3');
  h.textContent = t.alertsH;
  box.appendChild(h);
  const ul = document.createElement('ul');
  for(const it of j.items.slice(0, 6)){
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = /^https?:\/\//i.test(it.link || '') ? it.link : '#';
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = it.title;
    a.style.color = '#7dd3fc';
    li.appendChild(a);
    const sm = document.createElement('small');
    sm.textContent = ' — ' + it.source + (j.stale ? ' ' + t.staleTag : '');
    li.appendChild(sm);
    ul.appendChild(li);
  }
  box.appendChild(ul);
  const p = document.createElement('p');
  const sm2 = document.createElement('small');
  sm2.textContent = 'Fetched: ' + (j.fetched_at || '—') + ' · Live RSS';
  p.appendChild(sm2);
  box.appendChild(p);
}

export async function enrichDomainAge(input){
  const base = await apiBase();
  if(base === null) return;
  try{
    const r = await fetch(base + '/api/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input })
    });
    if(!r.ok) return;
    renderDomainAge(await r.json());
  }catch(e){ /* standalone — chup */ }
}

function renderDomainAge(j){
  const box = document.getElementById('ageBox');
  if(!box || !j || !j.domain || !j.domain_age) return;
  const t = getT();
  const p = document.createElement('p');
  if(j.domain_age.found && j.domain_age.registered_on){
    p.textContent = j.domain.host + ' — ' + t.ageReg + ' ' + j.domain_age.registered_on
      + ' (' + j.domain_age.age_days + ' ' + t.ageDays + ') · Source: RDAP (' + (j.domain_age.source || 'rdap.org') + ') · Fetched: ' + (j.domain_age.fetched_at || '—');
  } else if(!j.domain_age.found){
    p.textContent = j.domain.host + ' — ' + t.ageNotFound + ' · Source: RDAP (' + (j.domain_age.source || 'rdap.org') + ')';
  } else {
    return;
  }
  box.innerHTML = '';
  const h = document.createElement('h3');
  h.textContent = t.ageH;
  box.appendChild(h);
  box.appendChild(p);
}
