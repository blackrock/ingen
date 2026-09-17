//  SourceActionDialog — shown when the user connects/adds a source to an interface
//  that already has a base source. Offers two choices:
//    A) Create a new interface (independent pipeline with its own columns/output)
//    B) Merge into the current pipeline (auto-create a merge/union transform)

import { useEffect, useRef } from 'react';
import { GitMerge, Layers } from 'lucide-react';

/**
 * @param {{
 *   open: boolean,
 *   sourceId: string,
 *   onNewInterface: () => void,
 *   onMerge: () => void,
 *   onCancel: () => void,
 * }} props
 */
export default function SourceActionDialog({ open, sourceId, onNewInterface, onMerge, onCancel }) {
  const cancelRef = useRef(null);

  useEffect(() => {
    if (open) cancelRef.current?.focus();
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const handler = (e) => { if (e.key === 'Escape') onCancel(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [open, onCancel]);

  if (!open) return null;

  return (
    <div className="cdialog__backdrop" onClick={onCancel} role="presentation">
      <div
        className="cdialog cdialog--wide"
        role="dialog"
        aria-modal="true"
        aria-labelledby="srcaction-title"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="cdialog__title" id="srcaction-title">
          How should "{sourceId}" connect?
        </h2>
        <p className="cdialog__msg">
          This interface already has a base source. Choose how to wire the new source:
        </p>

        <div className="srcaction__choices">
          <button className="srcaction__card" onClick={onNewInterface}>
            <div className="srcaction__card-icon srcaction__card-icon--new">
              <Layers size={24} />
            </div>
            <div className="srcaction__card-text">
              <strong>New interface</strong>
              <span>Create a separate pipeline with its own columns, validations, and output.</span>
            </div>
          </button>

          <button className="srcaction__card" onClick={onMerge}>
            <div className="srcaction__card-icon srcaction__card-icon--merge">
              <GitMerge size={24} />
            </div>
            <div className="srcaction__card-text">
              <strong>Merge into current</strong>
              <span>Add a merge/union transform to combine this source with the existing pipeline.</span>
            </div>
          </button>
        </div>

        <div className="cdialog__actions">
          <button ref={cancelRef} className="btn btn--ghost" onClick={onCancel}>Cancel</button>
        </div>
      </div>
    </div>
  );
}
