"""Build the one-call browser payload for a page: gzip+base64 of the edit spec,
plus the JS that decodes it and applies it to the CodeMirror 6 editor.
Usage: python3 make_payload.py <slug> [dry|apply]  -> prints JS to out/<slug>.apply.js"""
import base64
import gzip
import hashlib
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / 'out'
slug = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else 'dry'
spec = json.loads((OUT / (slug + '.spec.json')).read_text())
raw = json.dumps(spec, ensure_ascii=False).encode('utf-8')
b64 = base64.b64encode(gzip.compress(raw, 9)).decode()
sha = hashlib.sha256(raw).hexdigest()[:16]

js = r'''
const B64 = "%(b64)s";
const MODE = "%(mode)s";
const bin = Uint8Array.from(atob(B64), c => c.charCodeAt(0));
const ds = new DecompressionStream('gzip'); const w = ds.writable.getWriter(); w.write(bin); w.close();
const rawBuf = await new Response(ds.readable).arrayBuffer();
const hashBuf = await crypto.subtle.digest('SHA-256', rawBuf);
const hex = [...new Uint8Array(hashBuf)].map(b => b.toString(16).padStart(2, '0')).join('').slice(0, 16);
if (hex !== "%(sha)s") throw new Error('payload hash mismatch ' + hex);
const spec = JSON.parse(new TextDecoder().decode(rawBuf));
const c = document.querySelector('.cm-content'); if (!c) throw new Error('no editor open');
const view = c.cmTile.view;
const src = view.state.doc.toString();
const ATTR = ' data-preserve-html-node="true"';
let s = src.split(ATTR).join('');
const report = [];
let ok = true;
for (const t of spec.text) { const n = s.split(t.find).length - 1; if (n !== t.count) { ok = false; report.push('TEXT x' + n + ': ' + t.find.slice(0, 70)); } }
const svgRe = tid => new RegExp('<svg[^>]*aria-labelledby="' + tid + ' [^"]*"[^>]*>[\\s\\S]*?</svg>', 'g');
for (const v of spec.svg) { const m = s.match(svgRe(v.tid)) || []; if (m.length !== 1) { ok = false; report.push('SVG ' + v.tid + ' x' + m.length); } }
const nSvg = (s.match(/<svg/g) || []).length, nH2 = (s.match(/<h2/g) || []).length;
let out = 'page ' + spec.slug + ' src ' + src.length + ' stripped ' + s.length + ' attrs ' + ((src.length - s.length) / ATTR.length) + ' svg ' + nSvg + ' h2 ' + nH2 + ' checks ' + (ok ? 'OK' : 'FAIL') + ' ' + report.join(' | ');
if (ok && MODE === 'apply') {
  for (const t of spec.text) s = s.split(t.find).join(t.replace);
  for (const v of spec.svg) s = s.replace(svgRe(v.tid), () => v.svg);
  view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: s } });
  const now = view.state.doc.toString();
  const nSvg2 = (now.match(/<svg/g) || []).length, nH22 = (now.match(/<h2/g) || []).length;
  window.__applied = { slug: spec.slug, len: now.length, nSvg: nSvg2, nH2: nH22 };
  localStorage.setItem('__newSrc_' + spec.slug, now);
  out += ' || APPLIED len ' + now.length + ' same ' + (now === s) + ' svg ' + nSvg2 + ' h2 ' + nH22;
}
out.replace(/[=&?%%]/g, '~').slice(0, 1000)
''' % {'b64': b64, 'mode': mode, 'sha': sha}
p = OUT / (slug + '.' + mode + '.js')
p.write_text(js)
print(p, 'b64', len(b64), 'js', len(js))
