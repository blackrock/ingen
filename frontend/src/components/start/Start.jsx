//  Start — the source-first entry. Shown by the config index when the first interface has no
//  sources yet: describe a source → choose inFlow/inChat → the workspace powers up on that source.
//  Supports adding MULTIPLE sources before entering the editor.

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, Trash2, FileText, Database, Globe, Braces } from 'lucide-react';

import { useConfig } from '../../state/ConfigContext.jsx';
import { useViewMode } from '../../state/ViewModeContext.jsx';
import { upsertSource, upsertInterface } from '../../models/configModel.js';
import { setColumns } from '../../lib/columnStore.js';
import SourceLoader from './SourceLoader.jsx';
import EntryOverlay from './EntryOverlay.jsx';

const TYPE_META = {
  file:         { icon: FileText,  color: '#3b82f6', label: 'File' },
  mysql:        { icon: Database,  color: '#f59e0b', label: 'MySQL' },
  api:          { icon: Globe,     color: '#8b5cf6', label: 'API' },
  json:         { icon: Braces,    color: '#10b981', label: 'JSON' },
};

export default function Start({ configId }) {
  const { model, updateModel } = useConfig();
  const { setViewMode } = useViewMode();
  const router = useRouter();
  const [step, setStep] = useState('source');       // 'source' | 'adding' | 'entry'
  const [pendingSources, setPendingSources] = useState([]); // [{ source, columns }, ...]

  const interfaceName = model?.interfaceOrder?.[0] ?? 'interface_1';

  const existingIds = [
    ...(model?.sourceOrder ?? []),
    ...pendingSources.map((p) => p.source.id),
  ];

  const onSource = (source, columns) => {
    setPendingSources((prev) => [...prev, { source, columns }]);
    setStep('source');
  };

  const removeSource = (idx) => {
    setPendingSources((prev) => prev.filter((_, i) => i !== idx));
  };

  const onChoose = (view) => {
    // Thread all pending sources through a single updateModel call so later sources
    // see the model already modified by earlier ones (avoids stale-closure data loss).
    updateModel((m) => {
      let next = m;
      for (const { source } of pendingSources) {
        next = upsertSource(next, source);
        const it = next.interfacesByName[interfaceName] ?? { sources: [], pre_processing: [], columns: [], post_processing: [], output: {} };
        next = upsertInterface(next, interfaceName, {
          ...it,
          sources: it.sources.includes(source.id) ? it.sources : [...it.sources, source.id],
        });
      }
      return next;
    });
    // Cache the fetched headers outside the updater — StrictMode double-invokes updaters, and this
    // writes to the shared column store rather than deriving the next model.
    for (const { source, columns } of pendingSources) setColumns(source.id, columns);
    setViewMode(view);
    router.push(`/configs/${configId}/interfaces/${interfaceName}`);
  };

  return (
    <div className="start">
      <div className="start__brandline">
        <span className="start__step">
          {step === 'entry' ? 'Step 2 · Choose your tool' : step === 'adding' ? 'Add another source' : 'Step 1 · Choose your data'}
        </span>
        <h1 className="start__title">
          {step === 'entry'
            ? `Build with ${pendingSources.length} source${pendingSources.length > 1 ? 's' : ''}`
            : 'Start with your data sources'}
        </h1>
      </div>

      {step === 'entry' ? (
        <EntryOverlay onChoose={onChoose} onBack={() => setStep('source')} />
      ) : step === 'adding' ? (
        <SourceLoader
          existingIds={existingIds}
          onSubmit={onSource}
          onCancel={() => setStep('source')}
          submitLabel="Add source"
        />
      ) : (
        <div className="start__sources">
          {pendingSources.length > 0 && (
            <div className="start__source-cards">
              {pendingSources.map(({ source }, i) => {
                const meta = TYPE_META[source.type] || TYPE_META.file;
                const Icon = meta.icon;
                return (
                  <div key={source.id} className="start__source-card">
                    <div className="start__source-card-left">
                      <div className="start__source-card-icon" style={{ backgroundColor: `${meta.color}18`, color: meta.color }}>
                        <Icon size={16} />
                      </div>
                      <div>
                        <div className="start__source-card-id">{source.id}</div>
                        <div className="start__source-card-type" style={{ color: meta.color }}>{meta.label}</div>
                      </div>
                    </div>
                    <button className="btn btn--ghost btn--sm" onClick={() => removeSource(i)} title="Remove">
                      <Trash2 size={14} />
                    </button>
                  </div>
                );
              })}
            </div>
          )}

          {pendingSources.length === 0 ? (
            <SourceLoader existingIds={existingIds} onSubmit={onSource} submitLabel="Add source" />
          ) : (
            <div className="start__actions">
              <button className="btn btn--ghost" onClick={() => setStep('adding')}>
                <Plus size={14} /> Add another source
              </button>
              <button className="btn btn--accent" onClick={() => setStep('entry')}>
                Continue with {pendingSources.length} source{pendingSources.length > 1 ? 's' : ''} →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
