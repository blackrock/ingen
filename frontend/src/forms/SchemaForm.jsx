//  InGen Studio — SchemaForm
//
//  Renders a form from a compact field-descriptor array, so source/pre-processor/formatter/output
//  forms are data, not bespoke JSX. Adding a backend field later = add a descriptor entry. This
//  schema-driven approach is the main defense against form duplication.
//
//  Descriptor: { key, label, kind, options?, optionsFrom?, placeholder?, help?, fields?, rows? }
//  kind ∈ text | number | select | tags | textarea | toggle | json | group
//  Dynamic option lists (e.g. sibling source ids) are resolved from `ctx` via `optionsFrom`.

import {
  TextField, NumberField, SelectField, TextAreaField, ToggleField, TagsField, JsonField,
} from './fields/Fields.jsx';

function resolveOptions(field, ctx) {
  if (field.options) return field.options;
  if (field.optionsFrom && ctx?.[field.optionsFrom]) return ctx[field.optionsFrom];
  return [];
}

function FieldRenderer({ field, value, onChange, ctx }) {
  const common = { label: field.label, help: field.help, value, onChange, placeholder: field.placeholder };
  switch (field.kind) {
    case 'number': return <NumberField {...common} />;
    case 'select': return <SelectField {...common} options={resolveOptions(field, ctx)} />;
    case 'tags': return <TagsField {...common} />;
    case 'textarea': return <TextAreaField {...common} rows={field.rows} />;
    case 'toggle': return <ToggleField {...common} />;
    case 'json': return <JsonField {...common} rows={field.rows} />;
    case 'group':
      return (
        <fieldset className="field__group">
          <legend className="field__grouplabel">{field.label}</legend>
          <SchemaForm
            schema={field.fields}
            value={value && typeof value === 'object' ? value : {}}
            onChange={onChange}
            ctx={ctx}
          />
        </fieldset>
      );
    case 'text':
    default:
      return <TextField {...common} />;
  }
}

/**
 * @param {{ schema: any[], value: object, onChange: (v:object)=>void, ctx?: object }} props
 */
export default function SchemaForm({ schema, value, onChange, ctx }) {
  const obj = value && typeof value === 'object' ? value : {};
  return (
    <div className="schemaform">
      {schema.map((field) => {
        if (field.visibleIf && !field.visibleIf(obj)) return null;
        return (
          <FieldRenderer
            key={field.key}
            field={field}
            ctx={ctx}
            value={obj[field.key]}
            onChange={(v) => {
              const next = { ...obj };
              if (v === undefined) delete next[field.key];
              else next[field.key] = v;
              onChange(next);
            }}
          />
        );
      })}
    </div>
  );
}
