import { useReactFlow } from 'reactflow';
import { Maximize2, LayoutDashboard, Undo2, Redo2, ZoomIn, ZoomOut } from 'lucide-react';

/**
 * Floating top-centre toolbar mirroring n8n's canvas controls.
 *
 * @param {{
 *   onAutoLayout: () => void,
 *   canUndo: boolean,
 *   canRedo: boolean,
 *   onUndo: () => void,
 *   onRedo: () => void,
 *   zoom: number,
 * }} props
 */
export default function GraphToolbar({ onAutoLayout, canUndo, canRedo, onUndo, onRedo, zoom }) {
  const { fitView, zoomIn, zoomOut } = useReactFlow();

  return (
    <div className="grapheditor__topbar">
      <button className="grapheditor__topbar-btn" title="Fit view (F)" onClick={() => fitView({ padding: 0.2, duration: 300 })}>
        <Maximize2 size={13} /> Fit view
      </button>
      <button className="grapheditor__topbar-btn" title="Auto layout" onClick={onAutoLayout}>
        <LayoutDashboard size={13} /> Layout
      </button>

      <div className="grapheditor__topbar-sep" />

      <button className="grapheditor__topbar-btn" title="Undo (Ctrl+Z)" onClick={onUndo} disabled={!canUndo}>
        <Undo2 size={13} />
      </button>
      <button className="grapheditor__topbar-btn" title="Redo (Ctrl+Shift+Z)" onClick={onRedo} disabled={!canRedo}>
        <Redo2 size={13} />
      </button>

      <div className="grapheditor__topbar-sep" />

      <button className="grapheditor__topbar-btn" title="Zoom out" onClick={() => zoomOut({ duration: 150 })}>
        <ZoomOut size={13} />
      </button>
      <span className="grapheditor__zoom-pct">{Math.round(zoom * 100)}%</span>
      <button className="grapheditor__topbar-btn" title="Zoom in" onClick={() => zoomIn({ duration: 150 })}>
        <ZoomIn size={13} />
      </button>
    </div>
  );
}
