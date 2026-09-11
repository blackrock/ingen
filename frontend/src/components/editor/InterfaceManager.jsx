//  InterfaceManager — rendered inside WorkspaceLayout above the NavRail.
//  Lets users: switch interfaces, rename them (inline), add new ones, and delete them.

import { useState, useRef, useLayoutEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Plus, Trash2, Pencil, Check, X } from 'lucide-react';

import { useConfig } from '../../state/ConfigContext.jsx';
import {
  createEmptyInterface,
  upsertInterface,
  removeInterface,
  renameInterface,
} from '../../models/configModel.js';
import ConfirmDialog from '../common/ConfirmDialog.jsx';

export default function InterfaceManager({ configId }) {
  const router = useRouter();
  const { interfaceName: activeIface } = useParams() || {};
  const { model, updateModel } = useConfig();

  const [editingName, setEditingName] = useState(null);  // name being renamed
  const [editValue, setEditValue] = useState('');
  const [confirmDel, setConfirmDel] = useState(null);    // name to delete
  const [addingNew, setAddingNew] = useState(false);
  const [newName, setNewName] = useState('');
  const inputRef = useRef(null);

  const interfaces = model?.interfaceOrder ?? [];
  const newNameTaken = Boolean(model?.interfacesByName?.[newName.trim()]);
  const newNameValid = newName.trim().length > 0 && !newNameTaken;

  // ── Rename ────────────────────────────────────────────────────────────────
  useLayoutEffect(() => {
    if (editingName) inputRef.current?.select();
  }, [editingName]);

  useLayoutEffect(() => {
    if (addingNew) inputRef.current?.focus();
  }, [addingNew]);

  const startRename = (name) => {
    setEditingName(name);
    setEditValue(name);
  };

  const commitRename = () => {
    const next = editValue.trim();
    if (next && next !== editingName) {
      try {
        updateModel((m) => renameInterface(m, editingName, next));
        // Navigate to the renamed interface if it was active.
        if (editingName === activeIface) {
          router.replace(`/configs/${configId}/interfaces/${encodeURIComponent(next)}`);
        }
      } catch { /* duplicate name — ignore */ }
    }
    setEditingName(null);
  };

  const cancelRename = () => setEditingName(null);

  // ── Add ───────────────────────────────────────────────────────────────────
  const commitAdd = () => {
    const name = newName.trim();
    if (!newNameValid) return;
    updateModel((m) => upsertInterface(m, name, createEmptyInterface()));
    setAddingNew(false);
    setNewName('');
    router.push(`/configs/${configId}/interfaces/${encodeURIComponent(name)}`);
  };

  // ── Delete ────────────────────────────────────────────────────────────────
  const doDelete = () => {
    if (!confirmDel) return;
    const wasActive = confirmDel === activeIface;
    updateModel((m) => removeInterface(m, confirmDel));
    setConfirmDel(null);
    if (wasActive) {
      const remaining = interfaces.filter((n) => n !== confirmDel);
      if (remaining.length > 0)
        router.replace(`/configs/${configId}/interfaces/${encodeURIComponent(remaining[0])}`);
      else
        router.replace(`/configs/${configId}`);
    }
  };

  if (interfaces.length === 0) return null;

  return (
    <div className="ifmgr">
      <div className="ifmgr__head">
        <span className="ifmgr__label">Interfaces</span>
        <button
          className="ifmgr__add-btn"
          title="Add interface"
          onClick={() => { setAddingNew(true); setNewName(''); }}
        >
          <Plus size={13} />
        </button>
      </div>

      <ul className="ifmgr__list">
        {interfaces.map((name) => (
          <li
            key={name}
            className={`ifmgr__item${name === activeIface ? ' ifmgr__item--active' : ''}`}
          >
            {editingName === name ? (
              <div className="ifmgr__rename">
                <input
                  ref={inputRef}
                  className="ifmgr__rename-input"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  onBlur={commitRename}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') commitRename();
                    if (e.key === 'Escape') cancelRename();
                  }}
                />
                <button className="ifmgr__icon-btn" onMouseDown={(e) => { e.preventDefault(); commitRename(); }} title="Confirm">
                  <Check size={12} />
                </button>
                <button className="ifmgr__icon-btn ifmgr__icon-btn--cancel" onMouseDown={(e) => { e.preventDefault(); cancelRename(); }} title="Cancel">
                  <X size={12} />
                </button>
              </div>
            ) : (
              <>
                <button
                  className="ifmgr__name-btn"
                  onClick={() => router.push(`/configs/${configId}/interfaces/${encodeURIComponent(name)}`)}
                >
                  {name}
                </button>
                <div className="ifmgr__actions">
                  <button className="ifmgr__icon-btn" title="Rename" onClick={() => startRename(name)}>
                    <Pencil size={11} />
                  </button>
                  <button
                    className="ifmgr__icon-btn ifmgr__icon-btn--danger"
                    title="Delete interface"
                    disabled={interfaces.length <= 1}
                    onClick={() => setConfirmDel(name)}
                  >
                    <Trash2 size={11} />
                  </button>
                </div>
              </>
            )}
          </li>
        ))}
      </ul>

      {addingNew && (
        <div className="ifmgr__new">
          <input
            ref={editingName ? undefined : inputRef}
            className={`ifmgr__rename-input${newNameTaken ? ' ifmgr__rename-input--err' : ''}`}
            placeholder="interface_name"
            value={newName}
            autoFocus
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && newNameValid) commitAdd();
              if (e.key === 'Escape') { setAddingNew(false); setNewName(''); }
            }}
          />
          <button className="ifmgr__icon-btn" disabled={!newNameValid} onMouseDown={(e) => { e.preventDefault(); commitAdd(); }} title="Create">
            <Check size={12} />
          </button>
          <button className="ifmgr__icon-btn ifmgr__icon-btn--cancel" onMouseDown={(e) => { e.preventDefault(); setAddingNew(false); setNewName(''); }} title="Cancel">
            <X size={12} />
          </button>
        </div>
      )}

      <ConfirmDialog
        open={Boolean(confirmDel)}
        title="Delete interface"
        message={`Delete interface "${confirmDel}"? All its columns, transforms, and output config will be lost. This can't be undone.`}
        confirmLabel="Delete"
        danger
        onConfirm={doDelete}
        onCancel={() => setConfirmDel(null)}
      />
    </div>
  );
}
