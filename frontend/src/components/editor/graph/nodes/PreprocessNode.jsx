import { Handle, Position } from 'reactflow';
import { Filter, Plug } from 'lucide-react';
import { STAGE, SOURCE_CONSUMERS, wiredSources } from '../graphConstants.js';
import { CustomNodeHeader, PropTable } from './NodeShared.jsx';

export function PreprocessNode({ data }) {
  const s = data.details || {};
  const spec = SOURCE_CONSUMERS[s.type];
  const wired = wiredSources(s);
  const rows = [{ key: 'type', value: s.type }];
  if (s.type === 'merge' || s.type === 'outer_join') {
    if (s.merge_type) rows.push({ key: 'join', value: s.merge_type });
    if (s.left_key && s.right_key) rows.push({ key: 'on', value: `${s.left_key} = ${s.right_key}` });
  }
  if (s.type === 'not_equals_filter') {
    const cols = s.cols || [];
    if (cols.length)
      rows.push({ key: 'filter', value: `${cols[0].col} ≠ ${(cols[0].val || []).join(',')}${cols.length > 1 ? ` +${cols.length - 1}` : ''}` });
  }
  if (s.type === 'aggregate') {
    rows.push({ key: 'group', value: (s.groupby?.cols || []).join(', ') || '—' });
  }

  return (
    <div className={`custom-node${data.selected ? ' custom-node--selected' : ''}`} style={{ borderLeft: `5px solid ${STAGE.transform}` }}>
      <Handle type="target" position={Position.Left} id="in" className="rf-handle rf-handle--in" />
      <CustomNodeHeader
        icon={<Filter size={14} />}
        title={`${data.index + 1}. ${data.label}`}
        type="Transform"
        color={STAGE.transform}
      />
      {spec && (
        <>
          <Handle type="target" position={Position.Top} id="src-in" className="rf-handle rf-handle--feed" title="Patch a source here" />
          <span className="custom-node__feedport" aria-hidden="true">
            <Plug size={9} /> source
          </span>
        </>
      )}
      <div className="custom-node__body">
        <PropTable rows={rows} />
        {spec && (
          <div className="custom-node__feeds">
            {wired.length ? (
              wired.map((sid) => <span key={sid} className="custom-node__feedchip">{sid}</span>)
            ) : (
              <span className="custom-node__feedhint">needs a {spec.tag} source</span>
            )}
          </div>
        )}
      </div>
      <Handle type="source" position={Position.Right} id="out" className="rf-handle rf-handle--out" />
    </div>
  );
}
