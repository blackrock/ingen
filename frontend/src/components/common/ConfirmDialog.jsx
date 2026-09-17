//  InGen Studio — ConfirmDialog
//
//  Drop-in replacement for window.confirm(). Renders a modal overlay with a title, message,
//  and Cancel / Confirm buttons. Confirm button can be styled as danger (red) or default.

import { useEffect, useRef } from 'react';

/**
 * @param {{
 *   open: boolean,
 *   title: string,
 *   message: string,
 *   confirmLabel?: string,
 *   danger?: boolean,
 *   onConfirm: () => void,
 *   onCancel: () => void,
 * }} props
 */
export default function ConfirmDialog({ open, title, message, confirmLabel = 'Confirm', danger = false, onConfirm, onCancel }) {
  const cancelRef = useRef(null);

  // Focus the cancel button when dialog opens (safe default).
  useEffect(() => {
    if (open) cancelRef.current?.focus();
  }, [open]);

  // Close on Escape key.
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
        className="cdialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="cdialog-title"
        aria-describedby="cdialog-msg"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="cdialog__title" id="cdialog-title">{title}</h2>
        <p className="cdialog__msg" id="cdialog-msg">{message}</p>
        <div className="cdialog__actions">
          <button ref={cancelRef} className="btn btn--ghost" onClick={onCancel}>Cancel</button>
          <button
            className={danger ? 'btn btn--danger' : 'btn btn--accent'}
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
