import { useEffect, useRef } from 'react';
import { Pencil, Trash2, Maximize2, LayoutDashboard, Unplug } from 'lucide-react';

/**
 * @param {{
 *   x: number, y: number,
 *   type: 'node' | 'edge' | 'pane',
 *   nodeId?: string,
 *   nodeType?: string,
 *   edgeId?: string,
 *   onClose: () => void,
 *   onEdit?: () => void,
 *   onDelete?: () => void,
 *   onDisconnect?: () => void,
 *   onFitView?: () => void,
 *   onAutoLayout?: () => void,
 * }} props
 */
export default function ContextMenu({
  x, y, type, onClose,
  onEdit, onDelete, onDisconnect,
  onFitView, onAutoLayout,
}) {
  const ref = useRef(null);

  // Close on outside click or Escape.
  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) onClose();
    };
    const keyHandler = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('mousedown', handler);
    document.addEventListener('keydown', keyHandler);
    return () => {
      document.removeEventListener('mousedown', handler);
      document.removeEventListener('keydown', keyHandler);
    };
  }, [onClose]);

  const item = (icon, label, fn, danger = false) => (
    <button
      className={`graph-ctxmenu__item${danger ? ' graph-ctxmenu__item--danger' : ''}`}
      onClick={() => { fn(); onClose(); }}
    >
      {icon} {label}
    </button>
  );

  return (
    <div ref={ref} className="graph-ctxmenu" style={{ left: x, top: y }}>
      {type === 'node' && (
        <div className="graph-ctxmenu__section">
          {onEdit    && item(<Pencil   size={13} />, 'Edit properties', onEdit)}
          {onDisconnect && item(<Unplug size={13} />, 'Disconnect all edges', onDisconnect)}
          {onDelete  && item(<Trash2   size={13} />, 'Delete node', onDelete, true)}
        </div>
      )}
      {type === 'edge' && (
        <div className="graph-ctxmenu__section">
          {onDelete && item(<Trash2 size={13} />, 'Delete connection', onDelete, true)}
        </div>
      )}
      {(type === 'pane' || type === 'node') && (
        <div className="graph-ctxmenu__section">
          {onFitView     && item(<Maximize2      size={13} />, 'Fit view',    onFitView)}
          {onAutoLayout  && item(<LayoutDashboard size={13} />, 'Auto layout', onAutoLayout)}
        </div>
      )}
    </div>
  );
}
