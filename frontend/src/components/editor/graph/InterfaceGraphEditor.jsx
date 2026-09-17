import { useEffect, useMemo, useCallback, useState, useRef } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Panel,
  MarkerType,
  useNodesState,
  useEdgesState,
  useReactFlow,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { X, Trash2 } from 'lucide-react';

import { useConfig } from '../../../state/ConfigContext.jsx';
import { useSourceActions } from '../../../hooks/useSourceActions.js';
import { useGraphSelection } from '../../../state/GraphSelectionContext.jsx';
import SchemaForm from '../../../forms/SchemaForm.jsx';
import { preProcessorSchema, PRE_PROCESSOR_SCHEMAS } from '../../../forms/schemas/preProcessorSchemas.js';
import { sourceSchema } from '../../../forms/schemas/sourceSchemas.js';
import { upsertSource, removeSource } from '../../../models/configModel.js';
import SourceActionDialog from '../../common/SourceActionDialog.jsx';

import SourcesTab from '../tabs/SourcesTab.jsx';
import ColumnsTab from '../tabs/ColumnsTab.jsx';
import PostProcessingTab from '../tabs/PostProcessingTab.jsx';
import ValidationsTab from '../tabs/ValidationsTab.jsx';
import OutputTab from '../tabs/OutputTab.jsx';

import { STAGE, SOURCE_CONSUMERS, wiredSources, SRC, PRE, FLOW_STYLE, CONN_STYLE } from './graphConstants.js';
import { SourceNode }     from './nodes/SourceNode.jsx';
import { PreprocessNode } from './nodes/PreprocessNode.jsx';
import { ColumnsNode }    from './nodes/ColumnsNode.jsx';
import { PostprocessNode } from './nodes/PostprocessNode.jsx';
import { ValidationsNode } from './nodes/ValidationsNode.jsx';
import { OutputNode }     from './nodes/OutputNode.jsx';
import { applyDagreLayout } from './useGraphLayout.js';
import ContextMenu from './ContextMenu.jsx';
import GraphToolbar from './GraphToolbar.jsx';

// These must be stable (defined outside the component) to avoid ReactFlow re-rendering all nodes.
const defaultEdgeOptions = { type: 'smoothstep' };
const nodeTypes = {
  source:      SourceNode,
  preprocess:  PreprocessNode,
  columns:     ColumnsNode,
  postprocess: PostprocessNode,
  validations: ValidationsNode,
  output:      OutputNode,
};

const miniMapColor = (n) =>
  STAGE[n.type === 'preprocess'  ? 'transform'
       : n.type === 'postprocess' ? 'post'
       : n.type === 'validations' ? 'validation'
       : n.type] || STAGE.output;

// ── Inner component (needs ReactFlowProvider wrapper for useReactFlow) ─────

function GraphEditorInner({ interfaceName, iface }) {
  const { model, updateInterface, updateModel, undo, redo, canUndo, canRedo } = useConfig();
  const { selectedNodeId, setSelectedNodeId } = useGraphSelection();
  const { fitView, getZoom } = useReactFlow();

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [zoom, setZoom] = useState(1);
  const [ctxMenu, setCtxMenu] = useState(null); // { x, y, type, nodeId?, nodeType?, edgeId? }
  // Track whether initial auto-layout was applied so we don't re-layout on every model change.
  const didInitLayout = useRef(false);

  // Merging a source adds nodes, so let the next render re-run the auto-layout.
  const { pendingSourceAction, setPendingSourceAction, handleNewInterface, handleMergeSource } =
    useSourceActions(interfaceName, { onMerged: () => { didInitLayout.current = false; } });

  // Leaving graph mode clears the shared selection.
  useEffect(() => () => setSelectedNodeId(null), [setSelectedNodeId]);

  //  fitView has to run after ReactFlow has committed the new node positions, so it is deferred by
  //  a tick. Track the pending timers and clear them on unmount — otherwise navigating away within
  //  the delay fires fitView against an unmounted ReactFlow instance.
  const fitTimers = useRef([]);
  const scheduleFitView = useCallback((delay) => {
    fitTimers.current.push(setTimeout(() => fitView({ padding: 0.2, duration: 300 }), delay));
  }, [fitView]);
  useEffect(() => () => {
    fitTimers.current.forEach(clearTimeout);
    fitTimers.current = [];
  }, []);

  const apply = useCallback((fn) => updateInterface(interfaceName, fn), [updateInterface, interfaceName]);

  // ── Build nodes + edges from the model ──────────────────────────────────
  useEffect(() => {
    const newNodes = [];
    const newEdges = [];

    const sources       = iface.sources        ?? [];
    const preProcesses  = iface.pre_processing  ?? [];
    const columns       = iface.columns         ?? [];
    const postProcess   = iface.post_processing ?? [];
    const validationCount = columns.reduce((n, c) => n + (c.validations?.length ?? 0), 0);
    const output        = iface.output ?? {};

    const baseSid    = sources[0];
    const referenced = new Set();
    preProcesses.forEach((step) => wiredSources(step).forEach((sid) => referenced.add(sid)));

    let colIndex = 0;
    const colWidth = 300;

    sources.forEach((sid, idx) => {
      newNodes.push({
        id: `${SRC}${sid}`,
        type: 'source',
        position: { x: colIndex * colWidth + 40, y: 60 + idx * 160 },
        data: {
          label: sid,
          details: model.sourcesById?.[sid],
          role: sid === baseSid ? 'base' : 'secondary',
          unused: sid !== baseSid && !referenced.has(sid),
          selected: false,
        },
      });
    });
    if (sources.length > 0) colIndex++;

    preProcesses.forEach((step, idx) => {
      newNodes.push({
        id: `${PRE}${idx}`,
        type: 'preprocess',
        position: { x: colIndex * colWidth + 40, y: 60 + idx * 160 },
        data: {
          label: PRE_PROCESSOR_SCHEMAS[step.type]?.label || step.type,
          index: idx,
          details: step,
          selected: false,
        },
      });
    });
    if (preProcesses.length > 0) colIndex++;

    const columnsNodeId = 'columns-node';
    newNodes.push({
      id: columnsNodeId,
      type: 'columns',
      position: { x: colIndex * colWidth + 40, y: 140 },
      data: {
        label: 'Columns Mapping',
        count: columns.length,
        columnNames: columns.map((c) => c.dest_col_name || c.src_col_name).filter(Boolean),
        selected: false,
      },
    });
    colIndex++;

    const postNodeId = 'post-node';
    const hasPost = postProcess.length > 0;
    if (hasPost) {
      newNodes.push({
        id: postNodeId,
        type: 'postprocess',
        position: { x: colIndex * colWidth + 40, y: 140 },
        data: { label: 'Post-processing', steps: postProcess, selected: false },
      });
      colIndex++;
    }

    const validationNodeId = 'validation-node';
    newNodes.push({
      id: validationNodeId,
      type: 'validations',
      position: { x: colIndex * colWidth + 40, y: 140 },
      data: { label: 'GE Validations', count: validationCount, selected: false },
    });
    colIndex++;

    const outputNodeId = 'output-node';
    newNodes.push({
      id: outputNodeId,
      type: 'output',
      position: { x: colIndex * colWidth + 40, y: 140 },
      data: { label: 'Output Destination', details: output, selected: false },
    });

    const flow = (id, source, target) => ({
      id, source, target,
      type: 'smoothstep',
      sourceHandle: 'out', targetHandle: 'in',
      animated: true, style: FLOW_STYLE,
      markerEnd: { type: MarkerType.ArrowClosed, color: STAGE.columns, width: 16, height: 16 },
    });

    const chainStart = preProcesses.length > 0 ? `${PRE}0` : columnsNodeId;
    if (baseSid) newEdges.push(flow(`flow-base-${chainStart}`, `${SRC}${baseSid}`, chainStart));

    preProcesses.forEach((_, idx) => {
      const next = idx < preProcesses.length - 1 ? `${PRE}${idx + 1}` : columnsNodeId;
      newEdges.push(flow(`flow-pre${idx}`, `${PRE}${idx}`, next));
    });

    let tail = columnsNodeId;
    if (hasPost) {
      newEdges.push(flow('flow-cols-post', columnsNodeId, postNodeId));
      tail = postNodeId;
    }
    newEdges.push(flow('flow-tail-val', tail, validationNodeId));
    newEdges.push(flow('flow-val-out', validationNodeId, outputNodeId));

    preProcesses.forEach((step, idx) => {
      const spec = SOURCE_CONSUMERS[step.type];
      if (!spec) return;
      wiredSources(step).forEach((sid) => {
        if (!model.sourcesById?.[sid] && !(iface.sources ?? []).includes(sid)) return;
        newEdges.push({
          id: `feed-${sid}-pre${idx}`,
          source: `${SRC}${sid}`, target: `${PRE}${idx}`,
          type: 'smoothstep',
          sourceHandle: 'out', targetHandle: 'src-in',
          data: { feed: true, sid, preIdx: idx },
          label: spec.tag,
          labelStyle: { fill: STAGE.source, fontSize: 10, fontFamily: 'var(--mono)', fontWeight: 600 },
          labelBgStyle: { fill: '#fff', stroke: STAGE.source, strokeWidth: 1 },
          labelBgPadding: [5, 3], labelBgBorderRadius: 5,
          style: { stroke: STAGE.source, strokeWidth: 1.6, strokeDasharray: '5 4' },
          markerEnd: { type: MarkerType.Arrow, color: STAGE.source },
        });
      });
    });

    // Apply dagre layout on first mount only; subsequent model changes keep user-dragged positions.
    if (!didInitLayout.current) {
      const laid = applyDagreLayout(newNodes, newEdges);
      setNodes(laid.nodes);
      setEdges(laid.edges);
      didInitLayout.current = true;
      scheduleFitView(60);
    } else {
      setNodes(newNodes);
      setEdges(newEdges);
    }
  }, [iface, model, setNodes, setEdges, scheduleFitView]);

  // Selection highlight (no position rebuild).
  useEffect(() => {
    setNodes((nds) =>
      nds.map((n) => ({ ...n, data: { ...n.data, selected: n.id === selectedNodeId } }))
    );
  }, [selectedNodeId, setNodes]);

  // Track zoom level for the toolbar display.
  const onMoveEnd = useCallback(() => setZoom(getZoom()), [getZoom]);

  // ── Connection logic ─────────────────────────────────────────────────────
  const feedConnectionSpec = useCallback((conn) => {
    if (!conn.source?.startsWith(SRC) || !conn.target?.startsWith(PRE)) return null;
    if (conn.targetHandle && conn.targetHandle !== 'src-in') return null;
    const idx = parseInt(conn.target.slice(PRE.length), 10);
    const step = iface.pre_processing?.[idx];
    const spec = step && SOURCE_CONSUMERS[step.type];
    if (!spec) return null;
    return { kind: 'feed', idx, sid: conn.source.slice(SRC.length), spec };
  }, [iface]);

  const chainConnectionSpec = useCallback((conn) => {
    if (!conn.source?.startsWith(SRC)) return null;
    const sid = conn.source.slice(SRC.length);
    if (conn.target?.startsWith(PRE) && (!conn.targetHandle || conn.targetHandle === 'in'))
      return { kind: 'chain', sid };
    if (['columns-node', 'post-node', 'validation-node', 'output-node'].includes(conn.target))
      return { kind: 'chain', sid };
    return null;
  }, []);

  const isValidConnection = useCallback(
    (conn) => Boolean(feedConnectionSpec(conn) || chainConnectionSpec(conn)),
    [feedConnectionSpec, chainConnectionSpec],
  );

  const onConnect = useCallback((conn) => {
    const feed = feedConnectionSpec(conn);
    if (feed) {
      const { idx, sid, spec } = feed;
      apply((it) => {
        const list = [...(it.pre_processing ?? [])];
        const cur = { ...list[idx] };
        if (spec.multi) {
          const arr = Array.isArray(cur[spec.param]) ? cur[spec.param] : cur[spec.param] ? [cur[spec.param]] : [];
          if (!arr.includes(sid)) cur[spec.param] = [...arr, sid];
        } else {
          cur[spec.param] = sid;
        }
        list[idx] = cur;
        return { ...it, pre_processing: list };
      });
      return;
    }
    const chain = chainConnectionSpec(conn);
    if (chain) {
      const currentSources = iface.sources ?? [];
      if (currentSources.length > 0 && !currentSources.includes(chain.sid)) {
        setPendingSourceAction({ sid: chain.sid });
      } else {
        apply((it) => {
          const cur = it.sources ?? [];
          if (cur.includes(chain.sid)) {
            return { ...it, sources: [chain.sid, ...cur.filter((s) => s !== chain.sid)] };
          }
          return { ...it, sources: [chain.sid, ...cur] };
        });
      }
    }
  }, [apply, iface, feedConnectionSpec, chainConnectionSpec, setPendingSourceAction]);

  // ── Source action handlers (new interface / merge) ─────────────────────────


  const onEdgesDelete = useCallback((deleted) => {
    deleted.forEach((e) => {
      if (!e.data?.feed) return;
      const { preIdx: idx, sid } = e.data;
      apply((it) => {
        const list = [...(it.pre_processing ?? [])];
        const step = list[idx];
        const spec = step && SOURCE_CONSUMERS[step.type];
        if (!spec) return it;
        const cur = { ...step };
        if (spec.multi) {
          const raw = cur[spec.param];
          const arr = Array.isArray(raw) ? raw : raw ? [raw] : [];
          cur[spec.param] = arr.filter((s) => s !== sid);
        } else if (cur[spec.param] === sid) {
          delete cur[spec.param];
        }
        list[idx] = cur;
        return { ...it, pre_processing: list };
      });
    });
  }, [apply]);

  // Delete selected nodes/edges via keyboard (Delete / Backspace handled by ReactFlow natively
  // through deleteKeyCode; onNodesDelete + onEdgesDelete handle the model side).
  const onNodesDelete = useCallback((deleted) => {
    deleted.forEach((n) => {
      if (n.id.startsWith(PRE)) {
        const idx = parseInt(n.id.slice(PRE.length), 10);
        apply((it) => ({ ...it, pre_processing: (it.pre_processing ?? []).filter((_, i) => i !== idx) }));
        setSelectedNodeId(null);
      }
    });
  }, [apply, setSelectedNodeId]);

  const onNodeClick = useCallback((_e, node) => {
    setSelectedNodeId((prev) => (prev === node.id ? null : node.id));
    setCtxMenu(null);
  }, [setSelectedNodeId]);

  // ── Drag-from-palette ───────────────────────────────────────────────────
  const pendingSelectRef = useRef(null);
  const onDrop = useCallback((event) => {
    event.preventDefault();
    const raw = event.dataTransfer.getData('application/reactflow');
    if (!raw) return;
    const nodeData = JSON.parse(raw);
    if (nodeData.type === 'transformNode' && nodeData.subtype) {
      const newIdx = iface.pre_processing?.length ?? 0;
      apply((i) => ({ ...i, pre_processing: [...(i.pre_processing ?? []), { type: nodeData.subtype }] }));
      pendingSelectRef.current = `${PRE}${newIdx}`;
    }
  }, [apply, iface]);

  // Use a ref+effect instead of setTimeout to defer selection after the drop re-render.
  useEffect(() => {
    if (pendingSelectRef.current) {
      setSelectedNodeId(pendingSelectRef.current);
      pendingSelectRef.current = null;
    }
  });

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  // ── Auto layout ─────────────────────────────────────────────────────────
  const handleAutoLayout = useCallback(() => {
    setNodes((nds) => {
      const { nodes: laid } = applyDagreLayout(nds, edges);
      return laid;
    });
    scheduleFitView(50);
  }, [setNodes, edges, scheduleFitView]);

  // ── Context menu handlers ───────────────────────────────────────────────
  const onNodeContextMenu = useCallback((e, node) => {
    e.preventDefault();
    setCtxMenu({ x: e.clientX, y: e.clientY, type: 'node', nodeId: node.id, nodeType: node.type });
  }, []);

  const onEdgeContextMenu = useCallback((e, edge) => {
    e.preventDefault();
    setCtxMenu({ x: e.clientX, y: e.clientY, type: 'edge', edgeId: edge.id, edgeData: edge.data });
  }, []);

  const onPaneContextMenu = useCallback((e) => {
    e.preventDefault();
    setCtxMenu({ x: e.clientX, y: e.clientY, type: 'pane' });
  }, []);

  const closeCtx = useCallback(() => setCtxMenu(null), []);

  const ctxEdit = ctxMenu?.nodeId
    ? () => { setSelectedNodeId(ctxMenu.nodeId); }
    : undefined;

  const ctxDelete = ctxMenu
    ? () => {
        if (ctxMenu.type === 'node') {
          if (ctxMenu.nodeId?.startsWith(SRC)) {
            const srcId = ctxMenu.nodeId.slice(SRC.length);
            updateModel((m) => removeSource(m, srcId));
            apply((it) => ({ ...it, sources: (it.sources ?? []).filter((s) => s !== srcId) }));
            setSelectedNodeId(null);
          } else if (ctxMenu.nodeId?.startsWith(PRE)) {
            const idx = parseInt(ctxMenu.nodeId.slice(PRE.length), 10);
            apply((it) => ({ ...it, pre_processing: (it.pre_processing ?? []).filter((_, i) => i !== idx) }));
            setSelectedNodeId(null);
          }
        }
        if (ctxMenu.type === 'edge' && ctxMenu.edgeData?.feed) {
          onEdgesDelete([{ data: ctxMenu.edgeData }]);
        }
        closeCtx();
      }
    : undefined;

  const ctxDisconnect = ctxMenu?.nodeId
    ? () => {
        setEdges((eds) => eds.filter((e) => e.source !== ctxMenu.nodeId && e.target !== ctxMenu.nodeId));
        closeCtx();
      }
    : undefined;

  // ── Keyboard shortcuts ───────────────────────────────────────────────────
  //  Graph-local only. Undo/redo are deliberately NOT bound here: useWorkspaceShortcuts (mounted
  //  by WorkspaceLayout, which wraps this editor) already binds Ctrl+Z / Ctrl+Y to the same
  //  useConfig() undo/redo. Binding them in both places popped two history entries per keypress.
  useEffect(() => {
    const handler = (e) => {
      const tag = document.activeElement?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA') return;
      if (e.key === 'f' || e.key === 'F') fitView({ padding: 0.2, duration: 300 });
      if (e.key === 'Escape') { setSelectedNodeId(null); closeCtx(); }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [fitView, setSelectedNodeId, closeCtx]);

  // ── Drawer content ───────────────────────────────────────────────────────
  const drawerContent = useMemo(() => {
    if (!selectedNodeId) return null;
    if (selectedNodeId === 'columns-node')
      return { title: 'Columns mapping',           Component: <ColumnsTab interfaceName={interfaceName} iface={iface} /> };
    if (selectedNodeId === 'post-node')
      return { title: 'Post-processing (pivot)',    Component: <PostProcessingTab interfaceName={interfaceName} iface={iface} /> };
    if (selectedNodeId === 'validation-node')
      return { title: 'Validation expectations',   Component: <ValidationsTab interfaceName={interfaceName} iface={iface} /> };
    if (selectedNodeId === 'output-node')
      return { title: 'Output destination',        Component: <OutputTab interfaceName={interfaceName} iface={iface} /> };
    if (selectedNodeId.startsWith('src-')) {
      const srcId  = selectedNodeId.slice(SRC.length);
      const srcDef = model.sourcesById?.[srcId];
      if (srcDef) {
        const schema = sourceSchema(srcDef.type);
        return {
          title: `Source: ${srcId}`,
          Component: (
            <div className="tabcontent">
              <div className="src-editor-header">
                <span className="src-editor-id">{srcId}</span>
                <span className="src-editor-type" style={{ color: STAGE.source }}>{srcDef.type}</span>
              </div>
              {schema.length > 0 ? (
                <SchemaForm
                  key={srcId}
                  schema={schema}
                  value={srcDef}
                  onChange={(next) => updateModel((m) => upsertSource(m, { ...next, id: srcId, type: srcDef.type }))}
                />
              ) : (
                <p className="tabcontent__hint">This source type has no configurable properties.</p>
              )}
              <hr style={{ border: 'none', borderTop: '1px solid var(--border-light)', margin: '16px 0' }} />
              <details>
                <summary style={{ fontSize: '12px', color: 'var(--text-muted)', cursor: 'pointer', marginBottom: 8 }}>All interface sources</summary>
                <SourcesTab interfaceName={interfaceName} iface={iface} />
              </details>
            </div>
          ),
        };
      }
      return { title: 'Interface sources', Component: <SourcesTab interfaceName={interfaceName} iface={iface} /> };
    }
    if (selectedNodeId.startsWith('pre-')) {
      const idx  = parseInt(selectedNodeId.split('-')[1], 10);
      const step = iface.pre_processing?.[idx];
      if (!step) return null;
      return {
        title: `Transform: ${PRE_PROCESSOR_SCHEMAS[step.type]?.label || step.type}`,
        Component: (
          <div className="tabcontent">
            <SchemaForm
              schema={preProcessorSchema(step.type)}
              value={step}
              ctx={{ sources: model.sourceOrder }}
              onChange={(next) =>
                apply((it) => {
                  const updated = [...(it.pre_processing ?? [])];
                  updated[idx] = { ...next, type: step.type };
                  return { ...it, pre_processing: updated };
                })
              }
            />
            <button
              className="btn btn--danger"
              style={{ width: '100%', marginTop: 16, justifyContent: 'center' }}
              onClick={() => {
                apply((it) => ({ ...it, pre_processing: (it.pre_processing ?? []).filter((_, i) => i !== idx) }));
                setSelectedNodeId(null);
              }}
            >
              <Trash2 size={14} /> Remove step
            </button>
          </div>
        ),
      };
    }
    return null;
  }, [selectedNodeId, iface, interfaceName, model, apply, setSelectedNodeId, updateModel]);

  return (
    <div className="grapheditor">
      <div className="grapheditor__canvas" onDrop={onDrop} onDragOver={onDragOver}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onEdgesDelete={onEdgesDelete}
          onNodesDelete={onNodesDelete}
          isValidConnection={isValidConnection}
          onNodeClick={onNodeClick}
          onNodeContextMenu={onNodeContextMenu}
          onEdgeContextMenu={onEdgeContextMenu}
          onPaneContextMenu={onPaneContextMenu}
          onPaneClick={closeCtx}
          onMoveEnd={onMoveEnd}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          snapToGrid
          snapGrid={[20, 20]}
          selectionOnDrag
          multiSelectionKeyCode="Shift"
          deleteKeyCode={['Backspace', 'Delete']}
          defaultEdgeOptions={defaultEdgeOptions}
          connectionMode="loose"
          connectionRadius={40}
          connectionLineStyle={CONN_STYLE}
        >
          <Background color={STAGE.columns} variant="dots" opacity={0.06} gap={20} size={1.5} />
          <Controls showInteractive />
          <MiniMap pannable zoomable nodeColor={miniMapColor} maskColor="rgba(248, 247, 255, 0.7)" />

          <Panel position="top-center" style={{ margin: 0 }}>
            <GraphToolbar
              onAutoLayout={handleAutoLayout}
              canUndo={canUndo}
              canRedo={canRedo}
              onUndo={undo}
              onRedo={redo}
              zoom={zoom}
            />
          </Panel>
        </ReactFlow>

        <div className="grapheditor__legend">
          <span className="grapheditor__legend-item"><i className="leg leg--flow" /> data flow</span>
          <span className="grapheditor__legend-item"><i className="leg leg--feed" /> source feed → YAML</span>
        </div>

        {ctxMenu && (
          <ContextMenu
            x={ctxMenu.x} y={ctxMenu.y}
            type={ctxMenu.type}
            nodeId={ctxMenu.nodeId}
            onClose={closeCtx}
            onEdit={ctxEdit}
            onDelete={
              ctxMenu?.type === 'edge' ||
              ctxMenu?.nodeId?.startsWith(SRC) ||
              ctxMenu?.nodeId?.startsWith(PRE)
                ? ctxDelete
                : undefined
            }
            onDisconnect={ctxDisconnect}
            onFitView={() => { fitView({ padding: 0.2, duration: 300 }); closeCtx(); }}
            onAutoLayout={() => { handleAutoLayout(); closeCtx(); }}
          />
        )}
      </div>

      {selectedNodeId && drawerContent && (
        <div className="grapheditor__drawer">
          <div className="grapheditor__drawer-head">
            <span className="grapheditor__drawer-title">{drawerContent.title}</span>
            <button className="grapheditor__drawer-close" onClick={() => setSelectedNodeId(null)}>
              <X size={16} />
            </button>
          </div>
          <div className="grapheditor__drawer-body">{drawerContent.Component}</div>
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

// ── Public export: wraps with ReactFlowProvider ────────────────────────────

export default function InterfaceGraphEditor(props) {
  return (
    <ReactFlowProvider>
      <GraphEditorInner {...props} />
    </ReactFlowProvider>
  );
}
