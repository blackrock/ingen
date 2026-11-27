//  InGen Studio — id helper
//
//  Single client-side unique-id generator. Opaque ids; collision-resistant via crypto.randomUUID
//  (available in all evergreen browsers and Node >= 19). Use everywhere instead of ad-hoc
//  Date.now()/Math.random() snippets so the format and collision guarantee live in one place.

/** @param {string} [prefix] */
export const makeId = (prefix = 'id') => `${prefix}_${crypto.randomUUID()}`;
