import dagre from '@dagrejs/dagre';

const NODE_WIDTH  = 260;
const NODE_HEIGHT = 120;

/**
 * Compute left-to-right dagre layout for the given nodes + edges.
 * Returns new arrays with updated `position` on each node.
 * Does NOT mutate the originals.
 *
 * @param {import('reactflow').Node[]} nodes
 * @param {import('reactflow').Edge[]} edges
 * @returns {{ nodes: import('reactflow').Node[], edges: import('reactflow').Edge[] }}
 */
export function applyDagreLayout(nodes, edges) {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: 'LR', nodesep: 60, ranksep: 120, marginx: 40, marginy: 40 });

  nodes.forEach((n) => {
    g.setNode(n.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  });
  edges.forEach((e) => {
    g.setEdge(e.source, e.target);
  });

  dagre.layout(g);

  const laid = nodes.map((n) => {
    const { x, y } = g.node(n.id);
    return { ...n, position: { x: x - NODE_WIDTH / 2, y: y - NODE_HEIGHT / 2 } };
  });

  return { nodes: laid, edges };
}
