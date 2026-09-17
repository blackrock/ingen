import { Handle, Position } from 'reactflow';
import { Columns } from 'lucide-react';
import { STAGE } from '../graphConstants.js';
import { CustomNodeHeader } from './NodeShared.jsx';

export function ColumnsNode({ data }) {
  const shown = (data.columnNames || []).slice(0, 5);
  const more = (data.count || 0) - shown.length;

  return (
    <div className={`custom-node${data.selected ? ' custom-node--selected' : ''}`} style={{ borderLeft: `5px solid ${STAGE.columns}` }}>
      <Handle type="target" position={Position.Left} id="in" className="rf-handle rf-handle--in" />
      <CustomNodeHeader icon={<Columns size={14} />} title="Columns" type={`${data.count} mapped`} color={STAGE.columns} />
      <div className="custom-node__body">
        <div className="custom-node__collist">
          {shown.map((name) => <span key={name} className="custom-node__colchip">{name}</span>)}
          {more > 0 && <span className="custom-node__colmore">+{more} more</span>}
          {data.count === 0 && <span className="custom-node__info">No columns defined</span>}
        </div>
      </div>
      <Handle type="source" position={Position.Right} id="out" className="rf-handle rf-handle--out" />
    </div>
  );
}
