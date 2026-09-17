//  Output editor — pick a writer type and configure its props via a schema-driven form. Covers the
//  supported writers (delimited_file, excel, json_writer, splitted_file). Edits flow to the live YAML.

import { useConfig } from '../../../state/ConfigContext.jsx';
import SchemaForm from '../../../forms/SchemaForm.jsx';
import { setField } from '../../../models/interfaceOps.js';
import { OUTPUT_SCHEMAS, OUTPUT_TYPE_OPTIONS, outputSchema } from '../../../forms/schemas/outputSchemas.js';

export default function OutputTab({ interfaceName, iface }) {
  const { updateInterface } = useConfig();
  const output = iface.output ?? {};
  const props = output.props && !Array.isArray(output.props) ? output.props : {};

  const apply = (fn) => updateInterface(interfaceName, fn);
  // Reset props on type change so fields from the previous writer don't leak into the new one's YAML.
  const setType = (type) => apply((it) => setField(it, 'output', type ? { type, props: {} } : {}));
  const setProps = (next) => apply((it) => setField(it, 'output', { type: output.type, props: next }));

  return (
    <div className="tabcontent">
      <p className="tabcontent__hint">How the formatted frame is persisted.</p>

      <select className="field__input field__input--wide" value={output.type ?? ''} onChange={(e) => setType(e.target.value)}>
        <option value="">— select writer —</option>
        {OUTPUT_TYPE_OPTIONS.map((t) => <option key={t} value={t}>{OUTPUT_SCHEMAS[t].label}</option>)}
      </select>

      {output.type && (
        <div className="outputform">
          <SchemaForm schema={outputSchema(output.type)} value={props} onChange={setProps} />
        </div>
      )}
    </div>
  );
}
