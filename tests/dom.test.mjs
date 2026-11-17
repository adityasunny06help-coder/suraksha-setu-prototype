// Suraksha Setu v4 — DOM-level tests (jsdom).
// Asli browser wale render paths: history (stored-XSS fix) + language switch.
import test from 'node:test';
import assert from 'node:assert/strict';
import { JSDOM } from 'jsdom';

const dom = new JSDOM(
  '<!DOCTYPE html><body><p id="tagline"></p><div id="histBox"></div></body>',
  { url: 'http://localhost/' }
);
global.window = dom.window;
global.document = dom.window.document;
global.localStorage = dom.window.localStorage;

const { saveHist, renderHist, setHistPickHandler } = await import('../js/history.js');
const { setLang } = await import('../js/i18n.js');

test('history stored-XSS fix: payload inert text banta hai, element NAHI', () => {
  saveHist('<img src=x onerror=alert(1)>', 85);
  const box = document.getElementById('histBox');
  assert.equal(box.querySelectorAll('img').length, 0, 'img element ban gaya — XSS zinda hai');
  assert.ok(!box.innerHTML.includes('<img'), 'raw payload HTML me leak hua');
  assert.ok(box.textContent.includes('<img src=x'), 'payload text ke roop me dikhna chahiye');
});

test('history click par pick handler chalta hai', () => {
  let picked = null;
  setHistPickHandler(q => { picked = q; });
  renderHist();
  const chip = document.querySelector('.hist');
  assert.ok(chip, 'history chip nahi mila');
  chip.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  assert.ok(picked && picked.startsWith('<img'));
});

test('pura UI language switch: Hindi label lagta hai, wapas Hinglish bhi', () => {
  setLang('hindi');
  let h = document.querySelector('#histBox h3');
  assert.ok(h && h.textContent.includes('पिछले'), 'Hindi hist label nahi laga');
  setLang('hing');
  h = document.querySelector('#histBox h3');
  assert.ok(h && h.textContent.includes('Pichhle'), 'Hinglish wapas nahi aaya');
});
