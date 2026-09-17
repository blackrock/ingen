import { Handle, Position } from 'reactflow';
import { ArrowRightLeft } from 'lucide-react';
import { STAGE } from '../graphConstants.js';
import { CustomNodeHeader, PropTable } from './NodeShared.jsx';

export function PostprocessNode({ data }) {
  const step = (data.steps || [])[0] || {};
  const pv = step.processing_values || {};
  const rows = [
    { key: 'type',  value: step.type    || null },
    { key: 'pivot', value: pv.pivot_col || null },
    { key: 'value', value: pv.value_col || null },
  ];

  return (
    <div className={`custom-node${data.selected ? ' custom-node--selected' : ''}`} style={{ borderLeft: `5px solid ${STAGE.post}` }}>
      <Handle type="target" position={Position.Left} id="in" className="rf-handle rf-handle--in" />
      <CustomNodeHeader icon={<ArrowRightLeft size={14} />} title="Post-processing" type="Reshape" color={STAGE.post} />
      <div className="custom-node__body">
        <PropTable rows={rows} />
      </div>
      <Handle type="source" position={Position.Right} id="out" className="rf-handle rf-handle--out" />
    </div>
  );
}
