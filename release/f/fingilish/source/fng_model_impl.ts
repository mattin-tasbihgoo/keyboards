// FingilishModel — custom-1.0 lexical model (Stage 4).
// ONE BRAIN: uses the converter's own norm/skel/translit (fng_model_fns.js,
// extracted verbatim from ConvertWord.call_js) and the converter's dictionary
// (fng_model_data.js). Deterministic; names included; the literal
// transliteration is ALWAYS offered as the last suggestion so the user can
// see exactly what they are spelling. (doc-04 L3/L4/L6)
class FingilishModel {
  punctuation: any = { insertAfterWord: " " };

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
    var lit = translit(lower);
    if (lit && lit !== '?' && out.indexOf(lit) < 0) { out.push(lit); }

    var P = [0.5, 0.22, 0.12, 0.08, 0.05];
    var dist: any[] = [];
    for (var i = 0; i < out.length && i < 5; i++) {
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
