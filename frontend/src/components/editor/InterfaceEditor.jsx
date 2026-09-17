//  InGen Studio — InterfaceEditor (PRIMARY screen)
//
//  Edits one interface at a time. Supports two view modes via ViewModeContext:
//    - Graph (inFlow): React Flow visual pipeline editor
//    - Chat (inChat): ChatGPT-like natural language conversational editor
//  The view switcher is in the brand bar — this component just reads the mode.

import { useParams } from 'next/navigation';

import { useConfig } from '../../state/ConfigContext.jsx';
import { useViewMode } from '../../state/ViewModeContext.jsx';

import dynamic from 'next/dynamic';
import InterfaceChatEditor from './chat/InterfaceChatEditor.jsx';

// Lazy-load the graph editor so reactflow (v11, not fully React 19 compatible) is only fetched
// when the user switches to graph mode — keeps the initial bundle clean and avoids the webpack
// module-resolution crash ("Cannot read properties of undefined (reading 'call')").
const InterfaceGraphEditor = dynamic(
  () => import('./graph/InterfaceGraphEditor.jsx'),
  { ssr: false, loading: () => <div className="placeholder">Loading graph editor…</div> },
);

export default function InterfaceEditor() {
  const { interfaceName } = useParams();
  const { model } = useConfig();
  const { viewMode } = useViewMode();

  const iface = model?.interfacesByName?.[interfaceName];

  if (!iface) {
    return <div className="placeholder">Interface "{interfaceName}" not found in this config.</div>;
  }

  return (
    <section className="editor editor--full">
      <div className="editor__panel">
        {viewMode === 'chat'
          ? <InterfaceChatEditor interfaceName={interfaceName} iface={iface} />
          : <InterfaceGraphEditor interfaceName={interfaceName} iface={iface} />}
      </div>
    </section>
  );
}
