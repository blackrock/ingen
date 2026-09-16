//  InGen Studio — HTTP ValidationService adapter
//
//  In HTTP mode, real validation RESULTS come from a run (GET /api/runs/{id}/validation, surfaced via
//  the RunRecord). `evaluate` is a pre-run preview of the expectations configured in the model — it
//  enumerates them client-side (no execution), matching the ValidationReport shape. This keeps the
//  ValidationService interface satisfied; the method is not on the HTTP run path (only the mock run
//  adapter calls evaluate internally).

import { ValidationService } from '../services/validationService.js';

export class HttpValidationAdapter extends ValidationService {
  constructor(client) {
    super();
    this.client = client; // reserved for a future /api/configs/validate-expectations endpoint
  }

  async evaluate(model, interfaceNames) {
    const names = interfaceNames?.length ? interfaceNames : model.interfaceOrder;
    const results = [];
    for (const name of names) {
      const iface = model.interfacesByName[name];
      if (!iface) continue;
      for (const col of iface.columns ?? []) {
        const column = col.dest_col_name || col.src_col_name || '(unnamed)';
        for (const v of col.validations ?? []) {
          results.push({
            interface: name,
            column,
            expectation: v.type,
            severity: v.severity ?? 'warning',
            status: 'passed', // preview only — real status comes from a run
            unexpectedCount: 0,
          });
        }
      }
    }
    const summary = { passed: results.length, failed: 0, warning: 0, total: results.length };
    return { results, summary };
  }
}
