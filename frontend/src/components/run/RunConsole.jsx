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
