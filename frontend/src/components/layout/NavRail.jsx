//  InGen Studio — NavRail (view-specific sidebar)
//
//  Left rail changes content based on the active view mode:
//    - Graph (inFlow): Node palette for drag-and-drop onto the canvas
//    - Chat (inChat):  Conversation history panel with session list
//  Collapsible via a toggle button at the bottom.

'use client';

import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  Database, FileOutput, Filter, ArrowRightLeft, ShieldCheck,
  Columns, Layers, Copy, GitMerge, Scissors, Table2, ListFilter, Plug,
  Plus, ChevronLeft, ChevronRight, MessageSquare, ChevronDown, X, Search
} from 'lucide-react';
import { useConfig } from '../../state/ConfigContext.jsx';
import { useSourceActions } from '../../hooks/useSourceActions.js';
import { useViewMode } from '../../state/ViewModeContext.jsx';
import { useChatSession } from '../../state/ChatSessionContext.jsx';
import { useGraphSelection } from '../../state/GraphSelectionContext.jsx';
import { getSessions } from '../../services/chatHistoryService.js';
import { buildPalette } from './navPalette.js';
import { upsertSource } from '../../models/configModel.js';
import { listAdd, setField } from '../../models/interfaceOps.js';
import { setColumns } from '../../lib/columnStore.js';
import InterfaceManager from '../editor/InterfaceManager.jsx';
import SourceActionDialog from '../common/SourceActionDialog.jsx';

// ─── inFlow Mode: Node Palette (draw.io-inspired) ───

// Icons are resolved here (navPalette.js is JSX-free so it can be unit-tested). Keyed by leaf
// subtype (sources/transforms/output) or action (columns/validations), with a per-group fallback.
const TRANSFORM_ICONS = {
  merge: <GitMerge size={15} />, outer_join: <GitMerge size={15} />,
  union: <Layers size={15} />, aggregate: <Table2 size={15} />,
  mask: <Scissors size={15} />, melt: <ArrowRightLeft size={15} />,
  filter: <ListFilter size={15} />, not_equals_filter: <Filter size={15} />,
  drop_duplicates: <Copy size={15} />, json_array_expander: <Columns size={15} />,
};
const SOURCE_ICONS = {
  file: <FileOutput size={15} />, mysql: <Database size={15} />, api: <Plug size={15} />,
  json: <Columns size={15} />,
};
const ACTION_ICONS = {
  add_column: <Columns size={15} />, add_validation: <ShieldCheck size={15} />,
};

function leafIcon(group, node) {
  if (group === 'Sources') return SOURCE_ICONS[node.subtype] || <Database size={15} />;
  if (group === 'Transforms') return TRANSFORM_ICONS[node.subtype] || <Filter size={15} />;
  if (group === 'Output') return <FileOutput size={15} />;
  return ACTION_ICONS[node.action] || <Filter size={15} />;
}

// Auto-id a new source: source_1, source_2, … avoiding collisions with existing ids.
function nextSourceId(model) {
  const taken = new Set(model.sourceOrder ?? []);
  let n = 1;
  while (taken.has(`source_${n}`)) n += 1;
  return `source_${n}`;
}

// Sensible defaults per source type — mirrors models/applyIntent.js so click-add matches chat-add.
const SOURCE_DEFAULTS = {
  file: (id) => ({ id, type: 'file', file_type: 'delimited_file', file_path: `data/${id}.csv` }),
  mysql: (id) => ({ id, type: 'mysql', database: '', query: 'SELECT * FROM table' }),
  api: (id) => ({ id, type: 'api', url: '', method: 'GET' }),
  json: (id) => ({ id, type: 'json' }),
};

function GraphPalette() {
  const { model, updateModel, updateInterface } = useConfig();
  const { setSelectedNodeId } = useGraphSelection();
  const { interfaceName } = useParams();
  const [query, setQuery] = useState('');
  const [collapsed, setCollapsed] = useState({});
  const [tip, setTip] = useState(null); // { node, note, x, y }
  const { pendingSourceAction, setPendingSourceAction, handleNewInterface, handleMergeSource } =
    useSourceActions(interfaceName, { onMerged: () => setSelectedNodeId(`src-${pendingSourceAction?.sid}`) });

  const onDragStart = (event, nodeData) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify(nodeData));
    event.dataTransfer.effectAllowed = 'move';
  };

  // Each handler mutates the model AND selects the resulting node, so the canvas opens its config
  // drawer — the same flow transforms already use. Click is the dependable, keyboard-accessible path
  // (drag works too for transforms but isn't reliable across browsers).
  const addTransform = (subtype) => {
    if (!interfaceName || !subtype) return;
    const newIdx = model.interfacesByName?.[interfaceName]?.pre_processing?.length ?? 0;
    updateInterface(interfaceName, (i) => ({
      ...i,
      pre_processing: [...(i.pre_processing ?? []), { type: subtype }],
    }));
    setSelectedNodeId(`pre-${newIdx}`);
  };

  const addSourceNode = (subtype) => {
    if (!interfaceName || !subtype) return;
    const id = nextSourceId(model);
    updateModel((m) => upsertSource(m, SOURCE_DEFAULTS[subtype](id)));
    setColumns(id, []);
    const currentSources = model.interfacesByName?.[interfaceName]?.sources ?? [];
    if (currentSources.length > 0) {
      setPendingSourceAction({ sid: id });
    } else {
      updateInterface(interfaceName, (it) => {
        const cur = it.sources ?? [];
        return cur.includes(id) ? it : { ...it, sources: [...cur, id] };
      });
      setSelectedNodeId(`src-${id}`);
    }
  };



  const addOutputNode = (subtype) => {
    if (!interfaceName || !subtype) return;
    updateInterface(interfaceName, (it) => setField(it, 'output', { type: subtype, props: it.output?.props ?? {} }));
    setSelectedNodeId('output-node');
  };

  const addColumnNode = () => {
    if (!interfaceName) return;
    updateInterface(interfaceName, (it) => listAdd(it, 'columns', { src_col_name: '', dest_col_name: '' }));
    setSelectedNodeId('columns-node');
  };

  // Validations are optional and attach per column; the existing drawer handles column + expectation
  // + severity, so we just open it.
  const openValidations = () => {
    if (!interfaceName) return;
    setSelectedNodeId('validation-node');
  };

  const runLeaf = (group, node) => {
    if (group === 'Sources') return addSourceNode(node.subtype);
    if (group === 'Transforms') return addTransform(node.subtype);
    if (group === 'Output') return addOutputNode(node.subtype);
    if (node.action === 'add_column') return addColumnNode();
    if (node.action === 'add_validation') return openValidations();
  };

  const q = query.trim().toLowerCase();
  const matches = (n) => !q || n.label.toLowerCase().includes(q) || (n.description || '').toLowerCase().includes(q);

  const showTip = (e, node, note) => {
    const r = e.currentTarget.getBoundingClientRect();
    setTip({ node, note, x: r.right + 10, y: r.top });
  };
  const hideTip = () => setTip(null);

  return (
    <div className="palette">
      <div className="palette__search">
        <Search size={14} className="palette__search-icon" aria-hidden="true" />
        <input
          className="palette__search-input"
          placeholder="Search nodes"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        {query && (
          <button className="palette__search-clear" title="Clear" onClick={() => setQuery('')}>
            <X size={13} />
          </button>
        )}
      </div>

      {buildPalette().map((group) => {
        const nodes = group.nodes.filter(matches);
        if (nodes.length === 0) return null;
        const isCollapsed = !q && collapsed[group.group];
        return (
          <div key={group.group} className="palette__group">
            <button
              className="palette__group-head"
              onClick={() => setCollapsed((c) => ({ ...c, [group.group]: !c[group.group] }))}
              aria-expanded={!isCollapsed}
            >
              {isCollapsed ? <ChevronRight size={13} /> : <ChevronDown size={13} />}
              <span>{group.group}</span>
              <span className="palette__group-count">{nodes.length}</span>
            </button>

            {!isCollapsed && (
              <div className="palette__nodes">
                {nodes.map((node) => (
                  <div
                    key={node.label}
                    className="palette-node palette-node--addable"
                    style={{ '--node-color': node.color }}
                    draggable={Boolean(node.draggable)}
                    onDragStart={node.draggable ? (e) => onDragStart(e, { type: 'transformNode', subtype: node.subtype }) : undefined}
                    role="button"
                    tabIndex={0}
                    onClick={() => runLeaf(group.group, node)}
                    onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); runLeaf(group.group, node); } }}
                    onMouseEnter={(e) => showTip(e, node, group.note)}
                    onFocus={(e) => showTip(e, node, group.note)}
                    onMouseLeave={hideTip}
                    onBlur={hideTip}
                  >
                    <span className="palette-node__icon" style={{ color: node.color }}>{leafIcon(group.group, node)}</span>
                    <span className="palette-node__text">
                      <span className="palette-node__label">{node.label}</span>
                      {node.writes && <span className="palette-node__sub">{node.writes}</span>}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}

      {tip && (
        <div className="palette-tip" style={{ left: tip.x, top: tip.y }} role="tooltip">
          <div className="palette-tip__title" style={{ color: tip.node.color }}>{tip.node.label}</div>
          {tip.node.description && <div className="palette-tip__desc">{tip.node.description}</div>}
          {tip.node.writes && (
            <div className="palette-tip__writes"><span>writes</span> <code>{tip.node.writes}</code></div>
          )}
          {tip.node.subtype ? (
            tip.node.hint && <div className="palette-tip__hint">{tip.node.hint}</div>
          ) : (
            tip.note && <div className="palette-tip__note">{tip.note}</div>
          )}
        </div>
      )}

      <SourceActionDialog
        open={Boolean(pendingSourceAction)}
        sourceId={pendingSourceAction?.sid ?? ''}
        onNewInterface={handleNewInterface}
        onMerge={handleMergeSource}
        onCancel={() => setPendingSourceAction(null)}
      />
    </div>
  );
}

// ─── Chat Mode: History Panel ───

function ChatHistory({ configId }) {
  const { model } = useConfig();
  const router = useRouter();
  const { interfaceName: activeInterface } = useParams();
  const { activeSessionId, requestNew, requestLoad } = useChatSession();
  const interfaces = model?.interfaceOrder ?? [];
  const base = `/configs/${configId}`;

  // Aggregate sessions from all interfaces, newest first.
  const allSessions = interfaces.flatMap((name) =>
    getSessions(name).map((s) => ({ ...s, interfaceName: name }))
  );
  allSessions.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

  const openSession = (s) => {
    // Switching to a conversation from another interface navigates there first; the editor then
    // honors the load command for its own interface.
    if (s.interfaceName !== activeInterface) router.push(`${base}/interfaces/${s.interfaceName}`);
    requestLoad(s.interfaceName, s.id);
  };

  return (
    <div className="navrail-chat">
      <div className="navrail-chat__title">Chat History</div>
      <button className="navrail-chat__new-btn" onClick={requestNew} disabled={!activeInterface}>
        <Plus size={14} /> New Chat
      </button>
      <ul className="navrail-chat__sessions">
        {allSessions.map((s) => (
          <li key={s.id}>
            <button
              className={`navrail-chat__session${s.id === activeSessionId ? ' navrail-chat__session--active' : ''}`}
              onClick={() => openSession(s)}
              aria-label={`Open chat: ${s.preview}`}
            >
              <span className="navrail-chat__session-preview">{s.preview}</span>
              <span className="navrail-chat__session-time">
                {new Date(s.createdAt).toLocaleDateString()} · {s.interfaceName}
              </span>
            </button>
          </li>
        ))}
        {allSessions.length === 0 && (
          <li className="navrail-chat__empty">
            <MessageSquare size={14} style={{ marginBottom: 4 }} />
            No conversations yet
          </li>
        )}
      </ul>
    </div>
  );
}

// ─── Main Component ───

export default function NavRail({ configId, collapsed, onToggleCollapse }) {
  const { viewMode } = useViewMode();

  return (
    <nav
      className={`navrail${collapsed ? ' navrail--collapsed' : ''}`}
      aria-label="Workspace navigation"
    >
      {!collapsed && <InterfaceManager configId={configId} />}
      {viewMode === 'graph' && <GraphPalette />}
      {viewMode === 'chat' && <ChatHistory configId={configId} />}

      <button
        className="navrail__collapse-btn"
        onClick={onToggleCollapse}
        title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
      </button>
    </nav>
  );
}
