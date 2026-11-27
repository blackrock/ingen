//  useWorkspaceShortcuts — global keyboard shortcuts active while in the workspace.
//  Ctrl+S  → flush the debounced autosave immediately
//  Ctrl+Z  → undo
//  Ctrl+Y / Ctrl+Shift+Z → redo
//
//  Does NOT intercept events originating from <input>, <textarea>, or <select> so typing
//  in form fields is never blocked.

import { useEffect } from 'react';

function isFormElement(el) {
  return el && ['INPUT', 'TEXTAREA', 'SELECT'].includes(el.tagName);
}

/**
 * @param {{ onSave?: () => void, onUndo?: () => void, onRedo?: () => void }} handlers
 */
export function useWorkspaceShortcuts({ onSave, onUndo, onRedo } = {}) {
  useEffect(() => {
    const handler = (e) => {
      if (isFormElement(document.activeElement)) return;
      const ctrl = e.ctrlKey || e.metaKey;
      if (!ctrl) return;

      if (e.key === 's') {
        e.preventDefault();
        onSave?.();
      } else if (e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        onUndo?.();
      } else if (e.key === 'y' || (e.key === 'z' && e.shiftKey)) {
        e.preventDefault();
        onRedo?.();
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onSave, onUndo, onRedo]);
}
