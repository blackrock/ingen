//  Stage timeline — per-interface row of pipeline stages (read → pre_process → [post_process] →
//  format → validate → write), each tile reflecting the latest stage status streamed from the run.
//  Derived purely from the event stream so it updates live as the mock execution progresses.

const STAGE_LABEL = {
  read: 'Read', pre_process: 'Pre', post_process: 'Post', format: 'Format', validate: 'Validate', write: 'Write',
};
const STATUS_CLASS = {
  running: 'stagetile--running', ok: 'stagetile--ok', warning: 'stagetile--warn',
  failed: 'stagetile--fail', skipped: 'stagetile--skip',
};

/** Fold stage events into { [interface]: { order: stage[], status: {stage:status} } }. */
function buildMatrix(events) {
  const byIface = new Map();
  for (const e of events) {
    if (e.type !== 'stage') continue;
    if (!byIface.has(e.interface)) byIface.set(e.interface, { order: [], status: {} });
    const entry = byIface.get(e.interface);
    if (!entry.order.includes(e.stage)) entry.order.push(e.stage);
    entry.status[e.stage] = e.status;
  }
  return byIface;
}

export default function StageTimeline({ events }) {
  const matrix = buildMatrix(events);
  if (matrix.size === 0) return <div className="emptyblock">No stages yet — start a run.</div>;

  return (
    <div className="timeline">
      {[...matrix.entries()].map(([iface, { order, status }]) => (
        <div key={iface} className="timeline__row">
          <span className="timeline__iface mono">{iface}</span>
          <div className="timeline__stages">
            {order.map((stage) => (
              <span key={stage} className={`stagetile ${STATUS_CLASS[status[stage]] ?? ''}`}>
                {STAGE_LABEL[stage] ?? stage}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
