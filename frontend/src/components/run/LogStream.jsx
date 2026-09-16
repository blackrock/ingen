//  Log stream — timestamped, levelled log lines from the run event stream, auto-scrolled to the
//  latest line. Mirrors the kind of output `python -m ingen` writes to its logger.

import { useEffect, useRef } from 'react';

const timeOf = (iso) => (iso ? iso.slice(11, 19) : '');

export default function LogStream({ events }) {
  const endRef = useRef(null);
  const logs = events.filter((e) => e.type === 'log');

  useEffect(() => { endRef.current?.scrollIntoView({ block: 'end' }); }, [logs.length]);

  if (logs.length === 0) return <div className="emptyblock">Logs will appear here during a run.</div>;

  return (
    <div className="logstream">
      {logs.map((e, i) => (
        <div key={e.ts ? `${e.ts}-${i}` : i} className={`logline logline--${e.level ?? 'info'}`}>
          <span className="logline__ts mono">{timeOf(e.ts)}</span>
          <span className={`logline__lvl logline__lvl--${e.level ?? 'info'}`}>{(e.level ?? 'info').toUpperCase()}</span>
          {e.interface && <span className="logline__scope mono">{e.interface}{e.stage ? `/${e.stage}` : ''}</span>}
          <span className="logline__msg">{e.message}</span>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
