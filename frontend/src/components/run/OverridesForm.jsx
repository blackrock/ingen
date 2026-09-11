//  Runtime overrides form — maps to the CLI args that don't mutate the saved YAML (run_date,
//  --interfaces subset, --override_params). Submitting starts a (mock) run.

import { useState } from 'react';
import { useConfig } from '../../state/ConfigContext.jsx';
import { JsonField } from '../../forms/fields/Fields.jsx';

export default function OverridesForm({ running, onRun, onCancel }) {
  const { model } = useConfig();
  const allInterfaces = model?.interfaceOrder ?? [];
  const [runDate, setRunDate] = useState('');
  const [selected, setSelected] = useState(() => new Set(allInterfaces));
  const [overrideParams, setOverrideParams] = useState(undefined);
  const [queryParams, setQueryParams] = useState(undefined);

  // The model often loads AFTER this form first mounts (allInterfaces was []), which left every
  // interface unchecked and the Run button disabled. Re-seed the selection (default = all) whenever
  // the set of interface NAMES changes, using React's render-phase "adjust state on prop change"
  // pattern (no effect — avoids a cascading-render lint and an extra commit). Keyed on the names so
  // unrelated model edits don't reset a user's manual selection.
  const ifaceKey = allInterfaces.join(' ');
  const [prevIfaceKey, setPrevIfaceKey] = useState(ifaceKey);
  if (prevIfaceKey !== ifaceKey) {
    setPrevIfaceKey(ifaceKey);
    setSelected(new Set(allInterfaces));
  }

  const toggle = (name) => setSelected((prev) => {
    const next = new Set(prev);
    if (next.has(name)) next.delete(name); else next.add(name);
    return next;
  });

  const submit = () => {
    const interfaces = allInterfaces.filter((n) => selected.has(n));
    onRun({
      ...(runDate ? { run_date: runDate } : {}),
      interfaces,
      ...(overrideParams ? { override_params: overrideParams } : {}),
      ...(queryParams ? { query_params: queryParams } : {}),
    });
  };

  return (
    <div className="overrides">
      <div className="overrides__row">
        <label className="field">
          <span className="field__label">run_date</span>
          <input className="field__input" type="date" value={runDate} onChange={(e) => setRunDate(e.target.value)} />
        </label>
        <div className="field">
          <span className="field__label">interfaces</span>
          <div className="overrides__ifaces">
            {allInterfaces.map((n) => (
              <label key={n} className="overrides__iface">
                <input type="checkbox" checked={selected.has(n)} onChange={() => toggle(n)} />
                <span className="mono">{n}</span>
              </label>
            ))}
          </div>
        </div>
      </div>
      <div className="overrides__row">
        <JsonField
          label="override_params"
          help="JSON object of runtime overrides passed to every interface (e.g. source paths, thresholds)"
          value={overrideParams}
          onChange={setOverrideParams}
          rows={2}
        />
        <JsonField
          label="query_params"
          help="JSON object of query parameters forwarded to API/DB sources"
          value={queryParams}
          onChange={setQueryParams}
          rows={2}
        />
      </div>
      <div className="overrides__actions">
        {running ? (
          <button className="btn btn--danger" onClick={onCancel}>Cancel</button>
        ) : (
          <button className="btn btn--accent" disabled={selected.size === 0} onClick={submit}>Run pipeline ▸</button>
        )}
      </div>
    </div>
  );
}
