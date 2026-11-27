//  SourceLoader — pick a source type, fill the fields that matter, (for files) drag-drop & upload.
//  One component, two entry points: the start screen AND the inFlow board's "+ Add source" modal.
//  Calls onSubmit(sourceObject, columns) once a valid source is described.

import { useState } from 'react';
import { FileText, Database, Globe, Braces, UploadCloud, ChevronDown, ChevronRight, Loader2 } from 'lucide-react';

import SchemaForm from '../../forms/SchemaForm.jsx';
import { requiredSourceFields, advancedSourceFields } from '../../forms/schemas/sourceSchemas.js';
import { SOURCE_TYPES, FILE_TYPES } from '../../models/constants.js';
import { uploadFile } from '../../services/fileService.js';

const TYPE_META = {
  file:         { icon: FileText,  color: '#3b82f6', label: 'File',          desc: 'CSV, Excel, XML, or JSON' },
  mysql:        { icon: Database,  color: '#f59e0b', label: 'MySQL',         desc: 'SQL query against a database' },
  api:          { icon: Globe,     color: '#8b5cf6', label: 'API',           desc: 'HTTP endpoint (REST / SOAP)' },
  json:         { icon: Braces,    color: '#10b981', label: 'JSON',          desc: 'Runtime JSON payload' },
};
const TYPES = Object.values(SOURCE_TYPES);

// Map a file extension to InGen's file_type so uploads land pre-configured.
const EXT_TO_FILETYPE = {
  csv: FILE_TYPES.DELIMITED_FILE, tsv: FILE_TYPES.DELIMITED_FILE, txt: FILE_TYPES.DELIMITED_FILE,
  xlsx: FILE_TYPES.EXCEL, xls: FILE_TYPES.EXCEL, xml: FILE_TYPES.XML, json: FILE_TYPES.JSON,
};

export default function SourceLoader({ existingIds = [], onSubmit, onCancel, submitLabel = 'Continue' }) {
  const [type, setType] = useState('file');
  const [id, setId] = useState('');
  const [fields, setFields] = useState({});       // type-specific body
  const [columns, setColumns] = useState([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [upload, setUpload] = useState(null);     // { name, rows, cached } | null
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const idTaken = existingIds.includes(id.trim());
  const required = requiredSourceFields(type);
  const advanced = advancedSourceFields(type);

  const missingRequired = required.some((f) => fields[f.key] == null || fields[f.key] === '');
  const canSubmit = id.trim().length > 0 && !idTaken && !missingRequired && !busy;

  // Reset body when switching type (fields don't carry across types).
  const pickType = (t) => { setType(t); setFields({}); setColumns([]); setUpload(null); setError(''); setShowAdvanced(false); };

  const handleFile = async (file) => {
    if (!file) return;
    setBusy(true); setError('');
    try {
      const res = await uploadFile(file);
      const ext = file.name.split('.').pop().toLowerCase();
      setFields((f) => ({ ...f, file_path: res.file_path, file_type: f.file_type || EXT_TO_FILETYPE[ext] }));
      setColumns(res.columns || []);
      setUpload({ name: file.name, rows: res.preview || [], cached: res.cached });
      if (!id.trim()) setId(file.name.replace(/\.[^.]+$/, '').replace(/\W+/g, '_'));
    } catch (e) {
      setError(e.message || 'Upload failed. Is the backend reachable?');
    } finally {
      setBusy(false);
    }
  };

  const submit = () => {
    if (!canSubmit) return;
    onSubmit?.({ id: id.trim(), type, ...fields }, columns);
  };

  const Meta = TYPE_META[type];

  return (
    <div className="srcloader">
      <div className="srcloader__types">
        {TYPES.map((t) => {
          const m = TYPE_META[t];
          const Icon = m.icon;
          return (
            <button
              key={t}
              type="button"
              className={`srctype${type === t ? ' srctype--active' : ''}`}
              style={{ '--c': m.color }}
              onClick={() => pickType(t)}
              aria-pressed={type === t}
            >
              <span className="srctype__icon"><Icon size={20} /></span>
              <span className="srctype__label">{m.label}</span>
              <span className="srctype__desc">{m.desc}</span>
            </button>
          );
        })}
      </div>

      <div className="srcloader__form">
        <label className="field">
          <span className="field__label">Source ID</span>
          <input
            className={`field__input${idTaken ? ' field__input--err' : ''}`}
            placeholder="e.g. trades_file"
            value={id}
            autoFocus
            onChange={(e) => setId(e.target.value)}
          />
          {idTaken && <span className="field__help field__help--err">A source with this ID already exists</span>}
        </label>

        {type === 'file' && (
          <Dropzone busy={busy} upload={upload} onFile={handleFile} />
        )}

        <SchemaForm schema={required} value={fields} onChange={setFields} />

        {advanced.length > 0 && (
          <>
            <button type="button" className="srcloader__advtoggle" onClick={() => setShowAdvanced((v) => !v)}>
              {showAdvanced ? <ChevronDown size={14} /> : <ChevronRight size={14} />} Advanced ({advanced.length})
            </button>
            {showAdvanced && <SchemaForm schema={advanced} value={fields} onChange={setFields} />}
          </>
        )}

        {error && <p className="srcloader__error">{error}</p>}
        {columns.length > 0 && (
          <p className="srcloader__cols">{columns.length} columns detected: <span className="mono">{columns.slice(0, 8).join(', ')}{columns.length > 8 ? '…' : ''}</span></p>
        )}

        <div className="srcloader__actions">
          {onCancel && <button type="button" className="btn btn--ghost" onClick={onCancel}>Cancel</button>}
          <button type="button" className="btn btn--accent" disabled={!canSubmit} onClick={submit} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <span className="srctype__icon" style={{ display: 'contents' }}><Meta.icon size={14} /></span> {submitLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

function Dropzone({ busy, upload, onFile }) {
  const [over, setOver] = useState(false);
  return (
    <div
      className={`dropzone${over ? ' dropzone--over' : ''}${upload ? ' dropzone--done' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setOver(true); }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => { e.preventDefault(); setOver(false); onFile(e.dataTransfer.files?.[0]); }}
    >
      <input id="srcfile" type="file" className="dropzone__input" onChange={(e) => onFile(e.target.files?.[0])} />
      <label htmlFor="srcfile" className="dropzone__label">
        {busy ? <Loader2 size={22} className="spin" /> : <UploadCloud size={22} />}
        {busy ? (
          <span>Parsing…</span>
        ) : upload ? (
          <span><strong>{upload.name}</strong> — {upload.rows.length} rows {upload.cached ? '(cached)' : 'loaded'}</span>
        ) : (
          <span>Drag a CSV/Excel here, or <u>browse</u></span>
        )}
      </label>
      {upload && upload.rows.length > 0 && (
        <div className="dropzone__preview">
          <table>
            {upload.rows.length > 1 && (
              <thead>
                <tr>{upload.rows[0].slice(0, 6).map((cell, j) => <th key={j}>{cell}</th>)}</tr>
              </thead>
            )}
            <tbody>
              {upload.rows.slice(upload.rows.length > 1 ? 1 : 0, 6).map((row, i) => (
                <tr key={i}>{row.slice(0, 6).map((cell, j) => <td key={j}>{cell}</td>)}</tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
