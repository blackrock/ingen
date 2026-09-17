'use client';

//  InGen Studio — YamlPreviewPanel
//
//  First-class, always-live YAML view. It renders `yaml` straight from ConfigContext, which derives
//  it from the REAL serializer (modelToYaml) on every model change — so editing any field updates
//  this panel immediately. Copy/download act on the same serialized text.
//
//  Lightweight, dependency-free syntax tinting + a line-number gutter. The tokenizer is line-based
//  and conservative (keys are simple identifiers in generated output), so it never mangles content —
//  worst case a line just renders in the default color.

import { useMemo, useState } from 'react';
import { useConfig } from '../../state/ConfigContext.jsx';

function download(filename, text) {
  const blob = new Blob([text], { type: 'text/yaml' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function valueClass(v) {
  if (/^-?\d+(\.\d+)?$/.test(v)) return 'tok-num';
  if (v === 'true' || v === 'false' || v === 'null') return 'tok-bool';
  if (v[0] === '"' || v[0] === "'") return 'tok-str';
  return 'tok-val';
}

/** Tokenize a single YAML line into colored spans (indentation preserved by white-space: pre). */
function tokens(line) {
  const m = line.match(/^(\s*)(.*)$/);
  const indent = m[1];
  let rest = m[2];
  if (rest === '') return indent || ' ';
  if (rest.startsWith('#')) return [indent, <span key="c" className="tok-comment">{rest}</span>];

  const parts = [indent];
  if (rest.startsWith('- ')) {
    parts.push(<span key="d" className="tok-dash">- </span>);
    rest = rest.slice(2);
  }
  // A quoted scalar is a single value, even if it contains ": " — don't split it into key:value.
  if (rest[0] === '"' || rest[0] === "'") {
    parts.push(<span key="v" className="tok-str">{rest}</span>);
    return parts;
  }
  const kv = rest.match(/^([^:\s][^:]*):(\s.*|)$/);
  if (kv) {
    parts.push(<span key="k" className="tok-key">{kv[1]}</span>, <span key="cl" className="tok-punct">:</span>);
    if (kv[2].trim()) parts.push(<span key="v" className={valueClass(kv[2].trim())}>{kv[2]}</span>);
  } else if (rest) {
    parts.push(<span key="v" className={valueClass(rest.trim())}>{rest}</span>);
  }
  return parts;
}

export default function YamlPreviewPanel() {
  const { yaml, model } = useConfig();
  const [copied, setCopied] = useState(false);
  const filename = `${model?.meta.id ?? 'config'}.yml`;

  const lines = useMemo(() => yaml.replace(/\n$/, '').split('\n'), [yaml]);

  // Track previous lines for diff highlighting. Held in state rather than a ref and recomputed
  // during render (React's "adjust state when a prop changes" pattern) so the comparison stays
  // correct under StrictMode double-invocation, which would corrupt a ref written during render.
  const [prevLines, setPrevLines] = useState(lines);
  const [changedSet, setChangedSet] = useState(() => new Set());
  if (prevLines !== lines) {
    const set = new Set();
    lines.forEach((line, i) => { if (line !== prevLines[i]) set.add(i); });
    // Also mark lines beyond old length as new.
    if (lines.length > prevLines.length) {
      for (let i = prevLines.length; i < lines.length; i++) set.add(i);
    }
    setPrevLines(lines);
    setChangedSet(set);
  }

  const copy = async () => {
    try {
      await navigator.clipboard?.writeText(yaml);
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    } catch {
      /* clipboard blocked — no-op */
    }
  };

  return (
    <aside className="yamlpanel" aria-label="YAML preview">
      <div className="yamlpanel__head">
        <span className="yamlpanel__title">{filename}</span>
        <span className="yamlpanel__live" title="Regenerated from the model on every edit">live</span>
        <div className="yamlpanel__actions">
          <button className={`yamlpanel__btn${copied ? ' yamlpanel__btn--ok' : ''}`} onClick={copy}>
            {copied ? 'Copied' : 'Copy'}
          </button>
          <button className="yamlpanel__btn" onClick={() => download(filename, yaml)}>
            Download
          </button>
        </div>
      </div>
      <div className="yamlpanel__code">
        {lines.map((line, i) => (
          <div className={`yamlpanel__line${changedSet.has(i) ? ' yamlpanel__line--changed' : ''}`} key={i}>
            <span className="yamlpanel__ln" aria-hidden="true">{i + 1}</span>
            <code className="yamlpanel__lc">{tokens(line)}</code>
          </div>
        ))}
      </div>
    </aside>
  );
}
