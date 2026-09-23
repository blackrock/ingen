//  Run Console (route element for /configs/:configId/run)
//
//  Composes the RunProvider and lays out the controls + live panels: stage timeline, log stream,
//  validation results. In mock mode RunService.simulate drives everything with no backend; in http
//  mode the same panels render the results streamed back from the FastAPI wrapper.

import { RunProvider, useRun } from '../../state/RunContext.jsx';
import { getAdapterMode } from '../../services/index.js';
import { ADAPTER_MODE } from '../../models/constants.js';
import OverridesForm from './OverridesForm.jsx';
import StageTimeline from './StageTimeline.jsx';
import LogStream from './LogStream.jsx';
import ValidationResults from './ValidationResults.jsx';

const STATUS_PILL = {
  success: 'pill--ok', partial: 'pill--warn', failed: 'pill--err',
};

// In HTTP mode the run is real (the wrapper executes `python -m ingen`); only mock mode is simulated.
const SUBTITLE = {
  [ADAPTER_MODE.HTTP]: 'Executes the config through the InGen backend. Logs and results are live.',
  [ADAPTER_MODE.MOCK]: 'Simulated execution — no backend. Logs and results are mocked.',
};

// First rows of each file the run wrote (backend `record.outputs`; absent in mock mode).
function OutputPreview({ outputs }) {
  return outputs.map((o) => (
    <div key={`${o.interface}:${o.path}`} className="outpreview">
      <div className="outpreview__head"><strong>{o.interface}</strong> → <span className="mono">{o.path}</span></div>
      <table>
        {o.columns.length > 0 && <thead><tr>{o.columns.map((c, i) => <th key={i}>{c}</th>)}</tr></thead>}
        <tbody>{o.rows.map((r, i) => <tr key={i}>{r.map((v, j) => <td key={j}>{v}</td>)}</tr>)}</tbody>
      </table>
    </div>
  ));
}

function Console() {
  const { status, events, record, start, cancel } = useRun();
  const subtitle = SUBTITLE[getAdapterMode()] ?? SUBTITLE[ADAPTER_MODE.MOCK];

  return (
    <section className="editor">
      <header className="editor__head editor__head--row">
        <div>
          <h1 className="editor__title">Run console</h1>
          <p className="editor__subtitle">{subtitle}</p>
        </div>
        {record && (
          <span className={`pill ${STATUS_PILL[record.status]}`}>
            {record.status} · {(record.durationMs / 1000).toFixed(2)}s
          </span>
        )}
      </header>

      <OverridesForm running={status === 'running'} onRun={start} onCancel={cancel} />

      <div className="runpanel">
        <h2 className="runpanel__title">Stages</h2>
        <StageTimeline events={events} />
      </div>

      {record?.outputs?.length > 0 && (
        <div className="runpanel">
          <h2 className="runpanel__title">Output preview</h2>
          <OutputPreview outputs={record.outputs} />
        </div>
      )}

      <div className="runpanel">
        <h2 className="runpanel__title">Logs</h2>
        <LogStream events={events} />
      </div>

      <div className="runpanel">
        <h2 className="runpanel__title">Validation results</h2>
        <ValidationResults report={record?.validation} />
      </div>
    </section>
  );
}

export default function RunConsole() {
  return (
    <RunProvider>
      <Console />
    </RunProvider>
  );
}
