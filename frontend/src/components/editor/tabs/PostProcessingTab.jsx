//  Post-processing tab — frame-level transforms applied after column formatting, before final
//  validation. The backend (ingen/post_processor) currently implements one processor: `pivot`,
//  shaped { type: 'pivot', processing_values: { pivot_col, value_col } }. This is a form surface,
//  not a graph.

import { useConfig } from '../../../state/ConfigContext.jsx';
import ListControls from '../../common/ListControls.jsx';
import { listAdd, listUpdate, listRemove, listMove } from '../../../models/interfaceOps.js';


function newStep() {
  return { type: 'pivot', processing_values: { pivot_col: '', value_col: '' } };
}

export default function PostProcessingTab({ interfaceName, iface }) {
  const { updateInterface } = useConfig();
  const steps = iface.post_processing ?? [];

  const apply = (fn) => updateInterface(interfaceName, fn);

  const setPivotField = (i, step, key, value) => {
    const processing_values = { ...(step.processing_values ?? {}), [key]: value || undefined };
    apply((it) => listUpdate(it, 'post_processing', i, { ...step, processing_values }));
  };

  return (
    <div className="tabcontent">
      <p className="tabcontent__hint">
        Applied after column formatting, before final validation. Pivot reshapes long rows into wide
        columns: every value in <span className="mono">pivot column</span> becomes a new column filled
        from <span className="mono">value column</span>.
      </p>

      <ol className="stepper">
        {steps.map((step, i) => (
          <li key={`${step.type}:${i}`} className="stepper__item stepper__item--editable">
            <span className="stepper__num">{i + 1}</span>
            <div className="stepper__body">
              <div className="stepper__row">
                <span className="chip chip--accent">{step.type}</span>
                <ListControls
                  index={i}
                  count={steps.length}
                  onMove={(d) => apply((it) => listMove(it, 'post_processing', i, d))}
                  onRemove={() => apply((it) => listRemove(it, 'post_processing', i))}
                />
              </div>
              {step.type === 'pivot' ? (
                <div className="schemaform">
                  <label className="field">
                    <span className="field__label">Pivot column</span>
                    <input
                      className="field__input"
                      placeholder="e.g. attribute"
                      value={step.processing_values?.pivot_col ?? ''}
                      onChange={(e) => setPivotField(i, step, 'pivot_col', e.target.value)}
                    />
                    <span className="field__help">Column whose distinct values become new columns.</span>
                  </label>
                  <label className="field">
                    <span className="field__label">Value column</span>
                    <input
                      className="field__input"
                      placeholder="e.g. amount"
                      value={step.processing_values?.value_col ?? ''}
                      onChange={(e) => setPivotField(i, step, 'value_col', e.target.value)}
                    />
                    <span className="field__help">Column whose values fill the new pivoted columns.</span>
                  </label>
                </div>
              ) : (
                <pre className="mono kvlist__json">{JSON.stringify(step.processing_values ?? {}, null, 2)}</pre>
              )}
            </div>
          </li>
        ))}
        {steps.length === 0 && <li className="stepper__empty">No post-processing configured.</li>}
      </ol>

      <div className="addbar" style={{ marginTop: 10 }}>
        <button
          className="btn btn--solid"
          onClick={() => apply((it) => listAdd(it, 'post_processing', newStep()))}
        >
          + Add pivot
        </button>
        <span className="muted" style={{ alignSelf: 'center' }}>
          Pivot is the only post-processor the backend supports today.
        </span>
      </div>
    </div>
  );
}
