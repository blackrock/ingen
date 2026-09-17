import { Handle, Position } from 'reactflow';
import { ShieldCheck } from 'lucide-react';
import { STAGE } from '../graphConstants.js';
import { CustomNodeHeader, PropTable } from './NodeShared.jsx';

export function ValidationsNode({ data }) {
  return (
    <div className={`custom-node${data.selected ? ' custom-node--selected' : ''}`} style={{ borderLeft: `5px solid ${STAGE.validation}` }}>
      <Handle type="target" position={Position.Left} id="in" className="rf-handle rf-handle--in" />
      <CustomNodeHeader icon={<ShieldCheck size={14} />} title="Validations" type="GE expectations" color={STAGE.validation} />
      <div className="custom-node__body">
        <PropTable rows={[{ key: 'count', value: data.count || 0 }]} />
      </div>
      <Handle type="source" position={Position.Right} id="out" className="rf-handle rf-handle--out" />
    </div>
  );
}
