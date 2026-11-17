// Suraksha Setu v4 — frontend tests (node --test).
// Sabse sakht gate: 6 built-in samples ke scores v3.1 se bilkul nahi badalne chahiye.
import test from 'node:test';
import assert from 'node:assert/strict';
import { scan, SAMPLES } from '../js/engine.js';
import { T } from '../js/i18n.js';
import { esc, buildResultHTML } from '../js/ui.js';

const EXPECTED = [85, 0, 85, 85, 30, 0];

test('regression gate: 6 samples ke scores unchanged (85/0/85/85/30/0)', () => {
  SAMPLES.forEach((s, i) => {
    const r = scan(s);
    assert.equal(r.score, EXPECTED[i], `sample ${i}: ${s.slice(0, 40)}`);
  });
});

test('parity extra: lookalike UPI handle hard 85 (Python test ke saath jod)', () => {
  assert.equal(scan('sbirefund@okhdfcbnak').score, 85);
});

test('v3.1 fix barkarar: official .apk par contradiction nahi', () => {
  const r = scan('https://www.sbi.bank.in/yono.apk');
  assert.equal(r.score, 0);
  assert.ok(r.reasons.every(x => (Array.isArray(x) ? x[0] : 0) === 0));
});

test('v3.1 fix barkarar: email ko UPI nahi samajhta', () => {
  const r = scan('abc@gmail.com');
  assert.equal(r.score, 0);
  assert.ok(!r.reasons.some(x => String(Array.isArray(x) ? x[1] : x).includes("Handle '@gmai")));
});

test('i18n: dono languages ke keys bilkul same, demos 6-6', () => {
  assert.deepEqual(Object.keys(T.hing).sort(), Object.keys(T.hindi).sort());
  assert.equal(T.hing.demos.length, 6);
  assert.equal(T.hindi.demos.length, 6);
});

test('esc: HTML special chars escape hote hain', () => {
  assert.equal(esc('<a href="x">&\''), '&lt;a href=&quot;x&quot;&gt;&amp;&#39;');
});

test('XSS discipline: result HTML me user ka payload raw nahi ghusta', () => {
  const payload = 'https://sbi-kyc-verify.top/login https://evil.example/"><svg onload=alert(1)>';
  const r = scan(payload);
  const html = buildResultHTML(r, payload);
  assert.ok(!html.includes('<svg onload'), 'raw <svg payload leak hua');
  assert.ok(html.includes('&lt;svg'), 'escaped roop maujood hona chahiye');
});

test('XSS discipline: attribute-breakout payloads bhi inert (deep-review Round 2)', () => {
  const payloads = [
    'check karo https://a.example/\'onmouseover=\'alert(1) https://sbi-kyc-verify.top',
    'https://a.example/x https://b.example/y"><svg onload=alert(1)>',
    'https://sbi-kyc-verify.top/<script>alert(1)</script>'
  ];
  for (const p of payloads) {
    const html = buildResultHTML(scan(p), p);
    assert.ok(!html.includes('<svg onload'), 'svg payload leak: ' + p.slice(0, 40));
    assert.ok(!html.includes('<script>alert'), 'script payload leak: ' + p.slice(0, 40));
    assert.ok(!html.includes('src=x onerror'), 'img payload leak: ' + p.slice(0, 40));
    assert.ok(!html.includes("'onmouseover='"), 'attribute breakout leak: ' + p.slice(0, 40));
  }
});
