//  Reusable reorder/delete controls for list rows (no drag-and-drop dependency — up/down satisfies
//  the reorder requirement and keeps React Flow reserved for multi-interface visualization only).

export default function ListControls({ index, count, onMove, onRemove }) {
  return (
    <div className="lctrls">
      <button className="lctrls__btn" title="Move up" aria-label="Move up" disabled={index === 0} onClick={() => onMove(-1)}>↑</button>
      <button className="lctrls__btn" title="Move down" aria-label="Move down" disabled={index === count - 1} onClick={() => onMove(1)}>↓</button>
      <button className="lctrls__btn lctrls__btn--del" title="Remove" aria-label="Remove" onClick={onRemove}>✕</button>
    </div>
  );
}
