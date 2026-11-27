import { Handle, Position } from 'reactflow';
import { FileOutput } from 'lucide-react';
import { STAGE, tr } from '../graphConstants.js';
import { CustomNodeHeader, PropTable } from './NodeShared.jsx';

export function OutputNode({ data }) {
  const d = data.details || {};
  const rows = [
    { key: 'type',  value: d.type },
    { key: 'path',  value: d.props?.path        ? tr(d.props.path)      : null },
    { key: 'sheet', value: d.props?.sheet_name  || null },
  ];

  return (
    <div className={`custom-node${data.selected ? ' custom-node--selected' : ''}`} style={{ borderLeft: `5px solid ${STAGE.output}` }}>
      <Handle type="target" position={Position.Left} id="in" className="rf-handle rf-handle--in" />
      <CustomNodeHeader icon={<FileOutput size={14} />} title="Output" type="Writer" color={STAGE.output} />
      <div className="custom-node__body">
        <PropTable rows={rows} />
      </div>
    </div>
  );
}
