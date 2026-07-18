// FingilishModel — custom-1.0 lexical model (Stage 4).
// ONE BRAIN: uses the converter's own norm/skel/translit (fng_model_fns.js,
// extracted verbatim from ConvertWord.call_js) and the converter's dictionary
// (fng_model_data.js). Deterministic; names included; the literal
// transliteration is ALWAYS offered as the last suggestion so the user can
// see exactly what they are spelling. (doc-04 L3/L4/L6)
class FingilishModel {
  punctuation: any = { insertAfterWord: " " };

  private _keys: string[] | null = null;
  private keyIndex(): string[] {
    if (!this._keys) { this._keys = Object.keys((FNG_DICT as any).exact).sort(); }
    return this._keys;
  }
  // first index whose key >= prefix (binary search)
  private lowerBound(keys: string[], prefix: string): number {
    var lo = 0, hi = keys.length;
    while (lo < hi) {
      var mid = (lo + hi) >> 1;
      if (keys[mid] < prefix) { lo = mid + 1; } else { hi = mid; }
    }
    return lo;
  }
  // dict entries whose key strictly extends `prefix`, closest (shortest) first
  private completions(prefix: string, exclude: string[], cap: number): string[] {
    if (prefix.length < 2) { return []; }
    var keys = this.keyIndex();
    var D: any = (FNG_DICT as any).exact;
    var found: { k: string, w: string }[] = [];
    for (var i = this.lowerBound(keys, prefix); i < keys.length; i++) {
      var k = keys[i];
      if (k.lastIndexOf(prefix, 0) !== 0) { break; }
      if (k === prefix) { continue; }
      var w = D[k];
      if (exclude.indexOf(w) < 0 && !found.some(function (f) { return f.w === w; })) {
        found.push({ k: k, w: w });
        if (found.length >= cap * 4) { break; }
      }
    }
    found.sort(function (x, y) { return x.k.length - y.k.length; });
    var out: string[] = [];
    for (var j = 0; j < found.length && out.length < cap; j++) { out.push(found[j].w); }
    return out;
  }

  configure(capabilities: any): any {
    return {
      leftContextCodePoints: (capabilities && capabilities.maxLeftContextCodePoints) || 64,
      rightContextCodePoints: 0
    };
  }

  private tokenOf(text: string): string {
    var m = (text || '').match(/((?:['\u201923])?[a-zA-Z][a-zA-Z'\u201923]*)$/);
    return m ? m[1] : '';
  }

  wordbreak(context: any): string {
    return this.tokenOf(context && context.left);
  }

  predict(transform: any, context: any): any {
    var left = (context && context.left) || '';
    var del = (transform && transform.deleteLeft) || 0;
    if (del > 0) { left = left.slice(0, Math.max(0, left.length - del)); }
    left += (transform && transform.insert) || '';

    var token = this.tokenOf(left);
    if (!token) { return []; }

    var hasOwn = Object.prototype.hasOwnProperty;
    var D: any = (FNG_DICT as any).exact;
    var S: any = (FNG_DICT as any).skel;
    var lower = token.toLowerCase();
    var bare = lower.replace(/['\u201923]/g, '');
    var aaIntent = bare.indexOf('aa') === 0;

    // Same tier order as the converter (ConvertWord.call_js main)
    var winner = '';
    var matchKey = '';
    if (hasOwn.call(D, lower)) { winner = D[lower]; matchKey = lower; }
    else if (hasOwn.call(D, bare)) { winner = D[bare]; matchKey = bare; }
    else if (!aaIntent) {
      var nw = norm(lower);
      if (hasOwn.call(D, nw)) { winner = D[nw]; matchKey = nw; }
      else {
        var sk = skel(nw);
        if (hasOwn.call(S, sk)) { winner = S[sk]; matchKey = sk; }
      }
    }

    var out: string[] = [];
    if (winner) { out.push(winner); }
    var altKeys = [lower, bare, matchKey];
    for (var ai = 0; ai < altKeys.length; ai++) {
      var ak = altKeys[ai];
      if (ak && hasOwn.call(FNG_ALTS as any, ak)) {
        var lst = (FNG_ALTS as any)[ak];
        for (var li = 0; li < lst.length; li++) {
          if (out.indexOf(lst[li]) < 0) { out.push(lst[li]); }
        }
        break;
      }
    }
    // Prefix completions: what this token could become (the multi-chip feel)
    var comps = this.completions(lower, out, 3);
    if (comps.length < 2 && bare !== lower) {
      comps = comps.concat(this.completions(bare, out.concat(comps), 3 - comps.length));
    }
    for (var ci = 0; ci < comps.length; ci++) { out.push(comps[ci]); }

    var lit = translit(lower);
    if (lit && lit !== '?' && out.indexOf(lit) < 0) { out.push(lit); }

    var P = [0.5, 0.2, 0.1, 0.07, 0.05, 0.04, 0.03, 0.02];
    var dist: any[] = [];
    for (var i = 0; i < out.length && i < 8; i++) {
      dist.push({
        p: P[i],
        sample: {
          transform: { insert: out[i], deleteLeft: token.length },
          displayAs: '\u2067' + out[i] + '\u2069'
        }
      });
    }
    return dist;
  }
}
