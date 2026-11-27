//  Mock ValidationService — derives deterministic, realistic results from the column validations
//  actually configured in the model. No execution. A stable string hash decides pass/fail so the
//  same config yields the same report (good for demos and history comparisons).

import { ValidationService } from '../services/validationService.js';

/** Stable 0..1 pseudo-random from a string. */
function seed01(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return ((h >>> 0) % 1000) / 1000;
}

export class MockValidationAdapter extends ValidationService {
  async evaluate(model, interfaceNames) {
    const names = interfaceNames?.length ? interfaceNames : model.interfaceOrder;
    /** @type {import('../services/validationService.js').ValidationResult[]} */
    const results = [];

    for (const name of names) {
      const iface = model.interfacesByName[name];
      if (!iface) continue;
      for (const col of iface.columns ?? []) {
        const column = col.dest_col_name || col.src_col_name || '(unnamed)';
        for (const v of col.validations ?? []) {
          const severity = v.severity ?? 'warning';
          const r = seed01(`${name}:${column}:${v.type}`);
          const fails = r > 0.7; // ~30% fail rate
          let status = 'passed';
          if (fails) status = severity === 'warning' ? 'warning' : 'failed';
          results.push({
            interface: name,
            column,
            expectation: v.type,
            severity,
            status,
            unexpectedCount: fails ? Math.ceil(r * 20) : 0,
          });
        }
      }
    }

    const summary = {
      passed: results.filter((x) => x.status === 'passed').length,
      failed: results.filter((x) => x.status === 'failed').length,
      warning: results.filter((x) => x.status === 'warning').length,
      total: results.length,
    };
    return { results, summary };
  }
}
