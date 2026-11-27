//  InGen Studio — inChat op applier
//
//  Turns the LLM's (or the regex fallback's) edit ops into model changes, deterministically. The op
//  vocabulary maps 1:1 onto the existing pure mutators — this file is a dispatch table, not new
//  pipeline logic — so the LLM never authors YAML; it only picks an op and fills the args, and the
//  serializer renders the YAML from the mutated model. Pure: returns a new model + a human reply.

import { upsertSource, upsertInterface, createEmptyInterface, removeSource } from './configModel.js';
import { listAdd, listUpdate, listRemove, setField } from './interfaceOps.js';
import { closest } from '../lib/fuzzy.js';
import { SOURCE_TYPES, OUTPUT_TYPES } from './constants.js';

const SOURCE_TYPE_LIST = Object.values(SOURCE_TYPES);
const OUTPUT_TYPE_LIST = Object.values(OUTPUT_TYPES);

const colName = (c) => c.dest_col_name || c.src_col_name;
const noChange = (model, reply) => ({ model, reply, changed: false });

/**
 * Apply ONE op to the model. Pure — never mutates its input.
 * @returns {{ model: object, reply: string, changed: boolean }}
 */
export function applyOp(model, interfaceName, knownColumns, op) {
  const iface = model.interfacesByName[interfaceName] ?? createEmptyInterface();

  switch (op?.op) {
    case 'add_columns': {
      const want = (op.cols ?? []).map((s) => String(s).trim()).filter(Boolean);
      if (!want.length) return noChange(model, "I didn't catch any column names to add.");
      const have = new Set((iface.columns ?? []).map(colName));
      const fresh = [];
      for (const c of want) if (!have.has(c)) { have.add(c); fresh.push(c); } // dedupe vs existing AND within the op
      if (!fresh.length) return noChange(model, `Those columns are already in the pipeline.`);
      let it = iface;
      for (const c of fresh) it = listAdd(it, 'columns', { src_col_name: c, dest_col_name: c });
      const n = fresh.length;
      return {
        model: upsertInterface(model, interfaceName, it),
        reply: `✅ Added ${n} column${n > 1 ? 's' : ''}: ${fresh.map((c) => `\`${c}\``).join(', ')}.`,
        changed: true,
      };
    }

    case 'rename_column': {
      const from = (op.from ?? '').trim();
      const to = (op.to ?? '').trim();
      if (!from || !to) return noChange(model, 'A rename needs both the current and the new column name.');
      const idx = (iface.columns ?? []).findIndex((c) => c.src_col_name === from || c.dest_col_name === from);
      const it = idx >= 0
        ? listUpdate(iface, 'columns', idx, { ...iface.columns[idx], src_col_name: iface.columns[idx].src_col_name ?? from, dest_col_name: to })
        : listAdd(iface, 'columns', { src_col_name: from, dest_col_name: to });
      return { model: upsertInterface(model, interfaceName, it), reply: `✅ Renamed \`${from}\` → \`${to}\`.`, changed: true };
    }

    case 'add_source': {
      if (!SOURCE_TYPE_LIST.includes(op.type)) return noChange(model, `I can only create sources of type: ${SOURCE_TYPE_LIST.join(', ')}.`);
      const name = (op.name ?? '').trim();
      if (!name) return noChange(model, 'A new source needs a name.');
      let m = upsertSource(model, {
        id: name,
        type: op.type,
        ...(op.type === 'file' ? { file_type: 'delimited_file', file_path: `data/${name}.csv` } : {}),
        ...(op.type === 'mysql' ? { database: 'default_db', query: 'SELECT * FROM table' } : {}),
      });
      const it = m.interfacesByName[interfaceName] ?? createEmptyInterface();
      const cur = it.sources ?? [];
      const it2 = cur.includes(name) ? it : { ...it, sources: [...cur, name] };
      m = upsertInterface(m, interfaceName, it2);
      return { model: m, reply: `✅ Added source \`${name}\` (\`${op.type}\`). It's on the board and in the YAML.`, changed: true };
    }

    case 'add_filter': {
      const col = (op.col ?? '').trim();
      if (!col) return noChange(model, 'A filter needs a column to filter on.');
      if (knownColumns.length && !knownColumns.includes(col)) {
        const guess = closest(col, knownColumns);
        return noChange(model, guess
          ? `I don't see a column \`${col}\`. Did you mean \`${guess}\`?`
          : `I don't see a column \`${col}\`. Known columns: ${knownColumns.join(', ')}.`);
      }
      const it = listAdd(iface, 'pre_processing', { type: 'not_equals_filter', cols: [{ col, val: [op.val] }] });
      return { model: upsertInterface(model, interfaceName, it), reply: `✅ Added a filter dropping rows where \`${col}\` = \`${op.val}\`.`, changed: true };
    }

    case 'set_output': {
      if (!OUTPUT_TYPE_LIST.includes(op.type)) return noChange(model, `I can only write to: ${OUTPUT_TYPE_LIST.join(', ')}.`);
      const props = (op.type === 'delimited_file' || op.type === 'excel')
        ? { path: `output/${interfaceName}.${op.type === 'excel' ? 'xlsx' : 'csv'}` }
        : { id: `out_${interfaceName}` };
      const it = setField(iface, 'output', { type: op.type, props });
      return { model: upsertInterface(model, interfaceName, it), reply: `✅ Output set to \`${op.type}\`. Check the YAML panel.`, changed: true };
    }

    case 'remove_column': {
      const target = (op.name ?? op.col ?? '').trim();
      if (!target) return noChange(model, 'Tell me which column to remove.');
      const cols = iface.columns ?? [];
      const idx = cols.findIndex((c) => c.src_col_name === target || c.dest_col_name === target);
      if (idx < 0) {
        const guess = closest(target, cols.map((c) => c.dest_col_name || c.src_col_name));
        return noChange(model, guess ? `I don't see \`${target}\`. Did you mean \`${guess}\`?` : `Column \`${target}\` not found.`);
      }
      return { model: upsertInterface(model, interfaceName, listRemove(iface, 'columns', idx)), reply: `✅ Removed column \`${target}\`.`, changed: true };
    }

    case 'remove_transform': {
      const steps = iface.pre_processing ?? [];
      const targetType = (op.type ?? '').trim();
      const targetIdx = typeof op.index === 'number' ? op.index : -1;
      const idx = targetIdx >= 0 ? targetIdx : steps.findIndex((s) => s.type === targetType);
      if (idx < 0 || idx >= steps.length) return noChange(model, `Couldn't find that transform to remove.`);
      const removed = steps[idx];
      return { model: upsertInterface(model, interfaceName, listRemove(iface, 'pre_processing', idx)), reply: `✅ Removed \`${removed.type}\` transform.`, changed: true };
    }

    case 'add_transform': {
      const validTypes = ['merge', 'outer_join', 'mask', 'not_equals_filter', 'union', 'melt', 'aggregate', 'drop_duplicates', 'json_array_expander'];
      const ttype = (op.type ?? '').trim();
      if (!validTypes.includes(ttype)) return noChange(model, `I can add these transforms: ${validTypes.join(', ')}.`);
      const it = listAdd(iface, 'pre_processing', { type: ttype });
      return { model: upsertInterface(model, interfaceName, it), reply: `✅ Added a \`${ttype}\` transform. Open the graph editor to configure it.`, changed: true };
    }

    case 'remove_source': {
      const srcId = (op.name ?? op.id ?? '').trim();
      if (!srcId) return noChange(model, 'Tell me which source to remove.');
      if (!model.sourcesById[srcId]) return noChange(model, `Source \`${srcId}\` doesn't exist.`);
      let m = removeSource(model, srcId);
      for (const [name, it] of Object.entries(m.interfacesByName)) {
        const filtered = (it.sources ?? []).filter((s) => s !== srcId);
        if (filtered.length !== (it.sources ?? []).length)
          m = { ...m, interfacesByName: { ...m.interfacesByName, [name]: { ...it, sources: filtered } } };
      }
      return { model: m, reply: `✅ Removed source \`${srcId}\` from the registry and all interfaces.`, changed: true };
    }

    case 'explain': {
      const srcs = (iface.sources ?? []).join(', ') || 'none';
      const cols = (iface.columns ?? []).length;
      const transforms = (iface.pre_processing ?? []).map((s) => s.type).join(', ') || 'none';
      const out = iface.output?.type || 'not set';
      return noChange(model,
        `**Pipeline: ${interfaceName}**\n\n` +
        `- **Sources:** ${srcs}\n` +
        `- **Transforms:** ${transforms}\n` +
        `- **Columns mapped:** ${cols}\n` +
        `- **Output:** ${out}\n\n` +
        `The YAML panel on the right shows the full serialized config.`
      );
    }

    default:
      return noChange(model, "I didn't catch a change there. Try a suggestion below, or e.g. `add columns id, status`.");
  }
}

/**
 * Apply an ordered list of ops, threading the model through each so later ops see earlier changes.
 * @returns {{ model: object, reply: string, changed: boolean }}
 */
export function applyOps(model, interfaceName, knownColumns, ops) {
  let m = model;
  const replies = [];
  let changed = false;
  for (const op of ops ?? []) {
    const r = applyOp(m, interfaceName, knownColumns, op);
    m = r.model;
    changed = changed || r.changed;
    replies.push(r.reply);
  }
  if (!replies.length) replies.push("I didn't catch a change there. Try a suggestion below.");
  return { model: m, reply: replies.join('\n'), changed };
}
