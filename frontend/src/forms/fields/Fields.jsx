//  InGen Studio — form field primitives
//
//  Small, controlled inputs used by the schema-driven SchemaForm and by bespoke editors. Each takes
//  a value + onChange and renders a labelled control. Kept deliberately plain (Phase focus is
//  function, not polish). TagsField/JsonField handle the array/object cases the InGen YAML needs.

import { useState, useEffect, useRef } from 'react';

export function Field({ label, help, children }) {
  return (
    <label className="field">
      {label && <span className="field__label">{label}</span>}
      {children}
      {help && <span className="field__help">{help}</span>}
    </label>
  );
}

export function TextField({ label, help, value, onChange, placeholder }) {
  return (
    <Field label={label} help={help}>
      <input
        className="field__input"
        value={value ?? ''}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value === '' ? undefined : e.target.value)}
      />
    </Field>
  );
}

export function NumberField({ label, help, value, onChange, placeholder }) {
  return (
    <Field label={label} help={help}>
      <input
        className="field__input"
        type="number"
        value={value ?? ''}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value === '' ? undefined : Number(e.target.value))}
      />
    </Field>
  );
}

export function SelectField({ label, help, value, onChange, options, allowEmpty = true }) {
  return (
    <Field label={label} help={help}>
      <select
        className="field__input"
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value === '' ? undefined : e.target.value)}
      >
        {allowEmpty && <option value="">—</option>}
        {options.map((opt) => {
          const v = typeof opt === 'string' ? opt : opt.value;
          const l = typeof opt === 'string' ? opt : opt.label;
          return <option key={v} value={v}>{l}</option>;
        })}
      </select>
    </Field>
  );
}

export function TextAreaField({ label, help, value, onChange, placeholder, rows = 3 }) {
  return (
    <Field label={label} help={help}>
      <textarea
        className="field__input field__input--area"
        rows={rows}
        value={value ?? ''}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value === '' ? undefined : e.target.value)}
      />
    </Field>
  );
}

export function ToggleField({ label, help, value, onChange }) {
  return (
    <label className="field field--toggle">
      <input type="checkbox" checked={Boolean(value)} onChange={(e) => onChange(e.target.checked)} />
      <span className="field__label">{label}</span>
      {help && <span className="field__help">{help}</span>}
    </label>
  );
}

/** Comma/whitespace separated string[] — used for column lists, keys, etc. */
export function TagsField({ label, help, value, onChange, placeholder }) {
  const text = Array.isArray(value) ? value.join(', ') : '';
  return (
    <Field label={label} help={help || 'comma-separated'}>
      <input
        className="field__input"
        value={text}
        placeholder={placeholder}
        onChange={(e) => {
          const arr = e.target.value.split(',').map((s) => s.trim()).filter(Boolean);
          onChange(arr.length ? arr : undefined);
        }}
      />
    </Field>
  );
}

/**
 * Free-form JSON value (object/array) for the long-tail of advanced fields. Keeps a local text
 * buffer (initialized from value) so intermediate invalid typing doesn't clobber the model and the
 * cursor isn't disturbed by reformatting; commits only valid JSON. The buffer is the source of
 * truth while mounted — callers that need to reset it pass a distinct React `key`.
 */
export function JsonField({ label, help, value, onChange, rows = 3 }) {
  const [text, setText] = useState(() => (value === undefined ? '' : JSON.stringify(value, null, 2)));
  const [error, setError] = useState(false);
  const lastCommitted = useRef(value);

  // Sync buffer when value changes externally (e.g. undo/redo) — only when the current
  // buffer is already valid (not mid-typing) and the new value differs from what we last wrote.
  useEffect(() => {
    if (value === lastCommitted.current) return;
    lastCommitted.current = value;
    setText(value === undefined ? '' : JSON.stringify(value, null, 2));
    setError(false);
  }, [value]);

  return (
    <Field label={label} help={help || 'JSON'}>
      <textarea
        className={`field__input field__input--area mono${error ? ' field__input--err' : ''}`}
        rows={rows}
        value={text}
        onChange={(e) => {
          const t = e.target.value;
          setText(t);
          if (t.trim() === '') { setError(false); lastCommitted.current = undefined; onChange(undefined); return; }
          try { const parsed = JSON.parse(t); lastCommitted.current = parsed; onChange(parsed); setError(false); } catch { setError(true); }
        }}
      />
      {error && <span className="field__help field__help--err">Invalid JSON — not saved</span>}
    </Field>
  );
}
