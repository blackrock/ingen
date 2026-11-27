//  Validations editor — great_expectations checks on the formatted frame, stored PER COLUMN under
//  columns[i].validations[] (matches ingen/validation/validations.py). Add/edit/remove with
//  expectation type, severity (→ action), and expectation args.

import { useState } from 'react';
import { useConfig } from '../../../state/ConfigContext.jsx';
import { useGraphSelection } from '../../../state/GraphSelectionContext.jsx';
import { colValAdd, colValUpdate, colValRemove } from '../../../models/interfaceOps.js';
import {
  ALL_EXPECTATIONS, SEVERITY_OPTIONS, SEVERITY_ACTION, VALIDATION_ARG_HINTS,
} from '../../../forms/schemas/validationSchemas.js';
import { JsonField } from '../../../forms/fields/Fields.jsx';

const colLabel = (c) => c.dest_col_name || c.src_col_name || '(unnamed)';

export default function ValidationsTab({ interfaceName, iface }) {
  const { updateInterface } = useConfig();
  const { setSelectedNodeId } = useGraphSelection();
  const columns = iface.columns ?? [];
  const [target, setTarget] = useState(0);
  const [expectation, setExpectation] = useState(ALL_EXPECTATIONS[0]);

  //  `target` is a column INDEX, so deleting a column can leave it pointing past the end (or at a
  //  different column than the user picked). Clamp on read rather than storing a corrected value,
  //  so the selection repairs itself without an extra render.
  const safeTarget = target < columns.length ? target : 0;

  const apply = (fn) => updateInterface(interfaceName, fn);

  // Flatten validations across columns into addressable rows.
  const rows = columns.flatMap((col, ci) =>
    (col.validations ?? []).map((v, vi) => ({ ci, vi, col, v })));

  return (
    <div className="tabcontent">
      <p className="tabcontent__hint">
        Expectations run on the formatted output. Severity decides the action:
        <span className="chip chip--warn">blocker</span> aborts ·
        <span className="chip chip--warn">critical</span> drops rows ·
        <span className="chip">warning</span> reports.
      </p>

      {columns.length === 0 ? (
        <div className="emptyblock">
          Add columns first — validations attach to a column.
          <button className="btn btn--ghost btn--xs" style={{ marginLeft: 8 }} onClick={() => setSelectedNodeId('columns-node')}>
            Go to Columns →
          </button>
        </div>
      ) : (
        <div className="addbar">
          <select className="field__input" value={safeTarget} onChange={(e) => setTarget(Number(e.target.value))}>
            {columns.map((c, i) => <option key={`${colLabel(c)}:${i}`} value={i}>{colLabel(c)}</option>)}
          </select>
          <select className="field__input field__input--wide" value={expectation} onChange={(e) => setExpectation(e.target.value)}>
            {ALL_EXPECTATIONS.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <button
            className="btn btn--solid"
            onClick={() => apply((it) => colValAdd(it, safeTarget, { type: expectation, severity: 'warning' }))}
          >
            + Add
          </button>
        </div>
      )}

      <div className="vlist">
        {rows.map(({ ci, vi, col, v }) => (
          <div key={`${ci}-${vi}`} className="vrow">
            <div className="vrow__head">
              <span className="chip">{colLabel(col)}</span>
              <span className="mono vrow__type">{v.type}</span>
              <select
                className="field__input vrow__sev"
                value={v.severity ?? 'warning'}
                onChange={(e) => apply((it) => colValUpdate(it, ci, vi, { ...v, severity: e.target.value }))}
              >
                {SEVERITY_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
              <span className="vrow__action muted">{SEVERITY_ACTION[v.severity ?? 'warning']}</span>
              <button className="lctrls__btn lctrls__btn--del" title="Remove validation" aria-label="Remove validation" onClick={() => apply((it) => colValRemove(it, ci, vi))}>✕</button>
            </div>
            <JsonField
              label="args"
              help={VALIDATION_ARG_HINTS[v.type] || 'no args'}
              value={v.args}
              rows={1}
              onChange={(args) => apply((it) => colValUpdate(it, ci, vi, { ...v, args }))}
            />
          </div>
        ))}
        {columns.length > 0 && rows.length === 0 && <div className="emptyblock">No validations configured.</div>}
      </div>
    </div>
  );
}
