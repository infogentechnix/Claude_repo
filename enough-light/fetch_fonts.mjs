// Downloads the film's fonts (SIL OFL 1.1) from Google Fonts into fonts/ and writes fonts.css.
// Run from this folder: node fetch_fonts.mjs
import fs from 'fs';
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36';
const get = async (u, o) => { const r = await fetch(u, o); if (!r.ok) throw new Error(`${u}: HTTP ${r.status}`); return r; };
const fams = [
  'family=Cormorant+Garamond:ital,wght@0,500;1,400;1,500',
  'family=Caveat:wght@500;600',
];
let out = '', n = 0;
fs.mkdirSync('fonts', { recursive: true });
for (const f of fams) {
  let css = await (await get(`https://fonts.googleapis.com/css2?${f}&display=block`, { headers: { 'User-Agent': UA } })).text();
  for (const u of [...new Set(css.match(/https:\/\/[^)]+/g) || [])]) {
    const name = `f${n++}.woff2`;
    fs.writeFileSync('fonts/' + name, Buffer.from(await (await get(u)).arrayBuffer()));
    css = css.split(u).join('fonts/' + name);
  }
  out += css;
}
fs.writeFileSync('fonts.css', out);
console.log('font files:', n);
