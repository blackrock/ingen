//  Validation results view — passed/failed/warning expectations with severity. Reused by the Run
//  Console and the History detail. Pure presentation of a ValidationReport.

const STATUS_CLASS = { passed: 'vres--pass', failed: 'vres--fail', warning: 'vres--warn' };

export default function ValidationResults({ report }) {
  if (!report) return <div className="emptyblock">Run the pipeline to see validation results.</div>;
  const { results, summary } = report;

  return (
    <div className="vres">
      <div className="vres__summary">
        <span className="pill pill--ok">{summary.passed} passed</span>
        <span className="pill pill--warn">{summary.warning} warning</span>
        <span className="pill pill--err">{summary.failed} failed</span>
        <span className="muted">of {summary.total}</span>
      </div>

      {results.length === 0 ? (
        <div className="emptyblock">No expectations configured on these interfaces.</div>
      ) : (
        <table className="dgrid">
          <thead>
            <tr><th>interface</th><th>column</th><th>expectation</th><th>severity</th><th>result</th></tr>
          </thead>
          <tbody>
            {results.map((r, i) => (
              <tr key={`${r.interface}:${r.column}:${r.expectation}:${i}`}>
                <td className="mono">{r.interface}</td>
                <td>{r.column}</td>
                <td className="mono">{r.expectation}</td>
                <td><span className="chip">{r.severity}</span></td>
                <td>
                  <span className={`vbadge ${STATUS_CLASS[r.status]}`}>
                    {r.status}{r.unexpectedCount ? ` · ${r.unexpectedCount}` : ''}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
