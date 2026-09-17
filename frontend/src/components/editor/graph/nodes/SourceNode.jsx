import { Handle, Position } from 'reactflow';
import { Database } from 'lucide-react';
import { STAGE, tr } from '../graphConstants.js';
import { CustomNodeHeader, PropTable } from './NodeShared.jsx';

export function SourceNode({ data }) {
  const d = data.details || {};
  const rows = [{ key: 'type', value: d.type }];
  if (d.file_type) rows.push({ key: 'format', value: d.file_type });
  if (d.file_path) rows.push({ key: 'path', value: tr(d.file_path) });
  if (d.database || d.db_token) rows.push({ key: 'db', value: d.database || d.db_token });
  if (d.url) rows.push({ key: 'url', value: tr(d.url) });

  const cls =
    'custom-node' +
    (data.selected ? ' custom-node--selected' : '') +
    (data.unused ? ' custom-node--unused' : '');

  return (
    <div className={cls} style={{ borderLeft: `5px solid ${STAGE.source}` }}>
      <CustomNodeHeader
        icon={<Database size={14} />}
        title={data.label}
        type={data.role === 'base' ? 'Base input' : 'Source'}
        color={STAGE.source}
      />
      <div className="custom-node__body">
        <PropTable rows={rows} />
        {data.unused && (
          <span className="custom-node__warn">Not wired — drag its port into a transform</span>
        )}
      </div>
      <Handle type="source" position={Position.Right} id="out" className="rf-handle rf-handle--out" />
    </div>
  );
}
