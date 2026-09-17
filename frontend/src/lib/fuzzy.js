//  Tiny Levenshtein + nearest-match, for "did you mean 'status'?" column-typo correction in inChat.

export function levenshtein(a, b) {
  const m = a.length, n = b.length;
  if (!m) return n;
  if (!n) return m;
  let prev = Array.from({ length: n + 1 }, (_, i) => i);
  for (let i = 1; i <= m; i++) {
    const cur = [i];
    for (let j = 1; j <= n; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost);
    }
    prev = cur;
  }
  return prev[n];
}

/** Closest option within `max` edits (case-insensitive), or null. */
export function closest(word, options, max = 2) {
  const w = String(word).toLowerCase();
  let best = null, bestD = Infinity;
  for (const opt of options) {
    const d = levenshtein(w, String(opt).toLowerCase());
    if (d < bestD) { bestD = d; best = opt; }
  }
  return bestD <= max ? best : null;
}
