#!/usr/bin/env node
// eval_translit.mjs — score algorithmic fallback heuristics against
// human-romanized ground truth (names datasets + elektito pairs).
// Usage: node eval_translit.mjs [--data DIR]
// Ground truth lives OUTSIDE the repo (default ~/Documents/Fingilish/namedata).
import fs from 'fs';
import path from 'path';
import os from 'os';

const dataDir = process.argv.includes('--data')
  ? process.argv[process.argv.indexOf('--data')+1]
  : path.join(os.homedir(), 'Documents/Fingilish/namedata');

// ---- translit: parameterized copy of the call_js fallback ----
// opts.aMode: 'always' (H0, ship today) | 'lastVowel' (H1)
// opts.suffixIan: strip -ian$ before stem analysis, append \u06CC\u0627\u0646
function translit(s, opts) {
  opts = opts || { aMode: 'always', suffixIan: false };
  s = s.toLowerCase();
  s = s.replace(/c(?=[eiy])/g, 's');
  s = s.replace(/c(?!h)/g, 'k');
  s = s.replace(/([^aeiou])\1+/g, '$1');

  var suffix = '';
  if (opts.suffixTable) {
    var SUF = [
      ['ian',  '\u06CC\u0627\u0646'],          // -ian  یان
      ['zadeh','\u0632\u0627\u062F\u0647'],    // -zadeh زاده
      ['zade', '\u0632\u0627\u062F\u0647'],
      ['pour', '\u067E\u0648\u0631'],           // -pour پور
      ['poor', '\u067E\u0648\u0631'],
      ['nejad','\u0646\u0698\u0627\u062F'],    // -nejad نژاد
      ['nezhad','\u0646\u0698\u0627\u062F'],
      ['abadi','\u0622\u0628\u0627\u062F\u06CC'], // -abadi آبادی
      ['vand', '\u0648\u0646\u062F'],           // -vand وند
      ['lou',  '\u0644\u0648'],                  // -lou لو
      ['loo',  '\u0644\u0648'],
      ['khah', '\u062E\u0648\u0627\u0647'],    // -khah خواه
      ['far',  '\u0641\u0631']                   // -far فر
    ];
    for (var si = 0; si < SUF.length; si++) {
      var suf = SUF[si][0];
      if (s.length > suf.length + 2 && s.slice(-suf.length) === suf) {
        s = s.slice(0, -suf.length);
        suffix = SUF[si][1];
        break;
      }
    }
  }
  else if (opts.suffixIan && /[^aeiou]ian$/.test(s) && s.length > 4) {
    s = s.slice(0, -3);
    suffix = '\u06CC\u0627\u0646'; // یان
  }

  // Precompute: index of the last vowel-run start (for aMode lastVowel)
  var lastVowelIdx = -1;
  for (var vi = s.length - 1; vi >= 0; vi--) {
    if ('aeiou'.indexOf(s[vi]) >= 0) { lastVowelIdx = vi; break; }
  }

  var out = '';
  var i = 0;
  var len = s.length;
  var di = {
    'sh':'\u0634','ch':'\u0686','zh':'\u0698','kh':'\u062E',
    'gh':'\u063A','ph':'\u0641'
  };
  var co = {
    'b':'\u0628','p':'\u067E','t':'\u062A','s':'\u0633',
    'j':'\u062C','d':'\u062F','z':'\u0632','r':'\u0631',
    'f':'\u0641','k':'\u06A9','g':'\u06AF','l':'\u0644',
    'm':'\u0645','n':'\u0646','v':'\u0648','w':'\u0648',
    'h':'\u0647','y':'\u06CC','q':'\u0642','x':'\u062E'
  };
  while (i < len) {
    if (i + 1 < len) {
      var pair = s[i] + s[i+1];
      if (di[pair]) { out += di[pair]; i += 2; continue; }
    }
    var c = s[i];
    if (co[c]) { out += co[c]; }
    else if (c === 'a') {
      if (i === 0 && i + 1 < len && s[i+1] === 'a') { out += '\u0622'; i += 2; continue; }
      if (i + 1 < len && s[i+1] === 'a') { out += '\u0627'; i += 2; continue; }
      if (i === 0) { out += '\u0627'; }
      else if (opts.aMode === 'always') { out += '\u0627'; }
      else if (opts.aMode === 'lastVowel') {
        // write ا only if this is the last vowel of the (suffix-stripped) word
        if (i === lastVowelIdx) { out += '\u0627'; }
        else if (opts.aBeforeNV && s[i+1] === 'n' &&
                 (i+2 >= len || 'aeiou'.indexOf(s[i+2]) >= 0)) {
          out += '\u0627';
        }
      }
    }
    else if (c === 'o') {
      if (i + 1 < len && s[i+1] === 'o') {
        out += (i === 0) ? '\u0627\u0648' : '\u0648';
        i += 2; continue;
      }
      if (i === 0) { out += '\u0627\u0648'; }
      else if (i === len - 1) { out += '\u0648'; }
    }
    else if (c === 'i') {
      if (i === 0) { out += '\u0627\u06CC'; }
      else { out += '\u06CC'; }
    }
    else if (c === 'e') {
      if (i + 1 < len && s[i+1] === 'e') {
        out += (i === 0) ? '\u0627\u06CC' : '\u06CC';
        i += 2; continue;
      }
      if (i === 0) { out += '\u0627'; }
      else if (i === len - 1) { out += '\u0647'; }
    }
    else if (c === 'u') { out += '\u0648'; }
    else if (c === '2') { out += '\u0621'; }
    else if (c === '3') { out += '\u0639'; }
    else if (c === "'" || c === '\u2019') { out += '\u0639'; }
    i++;
  }
  return (out + suffix) || s;
}

// ---- ground truth loaders ----
function cleanLatin(l) {
  l = l.toLowerCase().trim();
  if (/[^a-z']/.test(l)) return null; // reject spaces, hyphens, digits, mixed script
  if (l.length < 2 || l.length > 20) return null;
  return l;
}
function cleanPersian(p) {
  p = p.trim().replace(/[\u200c\u200d]/g, ''); // ZWNJ out for comparison
  if (!/^[\u0600-\u06FF]+$/.test(p)) return null;
  return p;
}
const sets = {};
// elektito: "latin persian" per line
sets.elektito = fs.readFileSync(path.join(dataDir,'elektito_f2p-dict.txt'),'utf8')
  .split('\n').map(l => l.trim().split(/\s+/)).filter(a => a.length === 2)
  .map(([lat,per]) => [cleanLatin(lat), cleanPersian(per)])
  .filter(([a,b]) => a && b);
// first names CSV: name,gender,english_name
sets.firstnames = fs.readFileSync(path.join(dataDir,'persian-gender-by-name.csv'),'utf8')
  .split('\n').slice(1).map(l => l.split(','))
  .filter(a => a.length === 3)
  .map(([per,,lat]) => [cleanLatin(lat), cleanPersian(per)])
  .filter(([a,b]) => a && b);
// surnames CSV: name,frequency,name_english — top 10k, clean english only
sets.surnames = fs.readFileSync(path.join(dataDir,'iranian-surname-frequencies.csv'),'utf8')
  .split('\n').slice(1, 10001).map(l => l.split(','))
  .filter(a => a.length === 3)
  .map(([per,,lat]) => [cleanLatin(lat), cleanPersian(per)])
  .filter(([a,b]) => a && b);
sets.surname_tail = fs.readFileSync(path.join(dataDir,'iranian-surname-frequencies.csv'),'utf8')
  .split('\n').slice(10001, 40001).map(l => l.split(','))
  .filter(a => a.length === 3)
  .map(([per,,lat]) => [cleanLatin(lat), cleanPersian(per)])
  .filter(([a,b]) => a && b);

// dedupe within each set on latin key (first wins)
for (const k of Object.keys(sets)) {
  const seen = new Set(); const out = [];
  for (const [lat,per] of sets[k]) {
    if (seen.has(lat)) continue; seen.add(lat); out.push([lat,per]);
  }
  sets[k] = out;
}

// ---- score ----
const heuristics = {
  'H0 always-alef (ship)':      { aMode:'always' },
  'H2 last-vowel + -ian$':      { aMode:'lastVowel', suffixIan:true  },
  'H7 lastV + aN + -ian$':      { aMode:'lastVowel', suffixIan:true,  aBeforeNV:true },
  'H8 lastV + aN + suftable':   { aMode:'lastVowel', suffixTable:true, aBeforeNV:true },
  'H9 always + suftable':       { aMode:'always',    suffixTable:true },
};
console.log('Ground truth sizes:', Object.fromEntries(Object.entries(sets).map(([k,v])=>[k,v.length])));
for (const [hname, opts] of Object.entries(heuristics)) {
  const line = [hname.padEnd(26)];
  let tot=0, totOk=0;
  for (const [sname, pairs] of Object.entries(sets)) {
    let ok=0;
    for (const [lat,per] of pairs) {
      if (translit(lat, opts).replace(/[\u200c]/g,'') === per) ok++;
    }
    tot+=pairs.length; totOk+=ok;
    line.push(`${sname}=${(100*ok/pairs.length).toFixed(1)}%`);
  }
  line.push(`ALL=${(100*totOk/tot).toFixed(1)}%`);
  console.log(line.join('  '));
}

// ---- spot check the six reported names + regression words under best guess ----
const spot = ['farzad','abbasian','ameneh','soraya','ava','azar','salam','zahra','baran','golshani','maryam','shirin'];
for (const hname of Object.keys(heuristics)) {
  console.log('\n' + hname);
  for (const w of spot) console.log(' ', w.padEnd(10), translit(w, heuristics[hname]));
}
