'use client';

//  InGen Studio — AppShell
//
//  Outermost frame: brand bar with the Graph/Chat view switcher at center, config name +
//  status on the right. The view mode is shared via ViewModeContext so the editor and sidebar
//  can read it. Workspace-specific controls (YAML toggle, Run) are also here.
//
//  Under Next this is the persistent client frame the root layout wraps around every route; the
//  routed page renders into {children} where the old react-router <Outlet> used to be.

import { useSyncExternalStore } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

import ErrorBoundary from '../common/ErrorBoundary.jsx';
import { ViewModeProvider, useViewMode } from '../../state/ViewModeContext.jsx';
import { ChatSessionProvider } from '../../state/ChatSessionContext.jsx';
import { GraphSelectionProvider } from '../../state/GraphSelectionContext.jsx';
import { ChevronLeft, GitBranch, MessageSquare } from 'lucide-react';
import { parentPath } from './navPaths.js';

function BrandBar() {
  const { viewMode, setViewMode } = useViewMode();
  const pathname = usePathname();
  const back = parentPath(pathname);
  const isWorkspace = pathname?.startsWith('/configs/');

  return (
    <header className="brandbar">
      <div className="brandbar__left">
        {back && (
          <Link href={back} className="btn btn--ghost brandbar__back" aria-label="Go back" title="Back">
            <ChevronLeft size={18} />
          </Link>
        )}
        <Link href="/" className="brandbar__mark">
          <div className="brandbar__mark-top">
            <span className="brandbar__glyph" aria-hidden="true">⌗</span>
            InGen<span className="brandbar__sub">Studio</span>
          </div>
          <span className="brandbar__tag">YAML Interface Authoring</span>
        </Link>
      </div>

      {isWorkspace && (
        <div className="brandbar__center">
          <div className="view-switcher" role="tablist">
            <button
              role="tab"
              aria-selected={viewMode === 'graph'}
              className={`view-switcher__btn${viewMode === 'graph' ? ' view-switcher__btn--active' : ''}`}
              onClick={() => setViewMode('graph')}
            >
              <GitBranch size={14} />
              inFlow
            </button>
            <button
              role="tab"
              aria-selected={viewMode === 'chat'}
              className={`view-switcher__btn${viewMode === 'chat' ? ' view-switcher__btn--active' : ''}`}
              onClick={() => setViewMode('chat')}
            >
              <MessageSquare size={14} />
              inChat
            </button>
          </div>
        </div>
      )}

      <div className="brandbar__right" id="brandbar-right-portal">
        {/* WorkspaceLayout injects config name, save pill, YAML toggle here via portal */}
      </div>
    </header>
  );
}

//  This is a pure client SPA (localStorage-backed store, reactflow, portals). Gate the routed
//  content so it mounts only on the client: server render and the first client render both show the
//  same fallback (no hydration mismatch), then the real tree mounts. The brand bar uses no browser
//  APIs, so it renders on the server for an instant, branded first paint.
//
//  IMPORTANT: this boundary is NOT keyed on the route. ConfigProvider lives below here (in the
//  config layout), so keying on pathname would remount the provider on every navigation — which
//  reloads the persisted model and discards any not-yet-autosaved edit (e.g. a just-added
//  interface). Per-route error reset is handled lower down, below the provider, in WorkspaceLayout.

//  The "is the client live" store never changes after hydration, so there is nothing to subscribe
//  to — this returns a no-op unsubscribe. Module-level so the reference stays stable across renders.
const subscribeNoop = () => () => {};

function AppBody({ children }) {
  //  useSyncExternalStore is the hydration-safe way to ask "are we on the client yet?": the server
  //  snapshot is false and the client snapshot is true, so server render and first client render
  //  agree (no hydration mismatch) and the real tree mounts on the next pass. Doing this with
  //  useState + useEffect would set state synchronously in an effect on every mount.
  const mounted = useSyncExternalStore(subscribeNoop, () => true, () => false);

  return (
    <div className="app-shell__body">
      <ErrorBoundary>
        {mounted ? children : <div className="placeholder">Loading…</div>}
      </ErrorBoundary>
    </div>
  );
}

export default function AppShell({ children }) {
  return (
    <ViewModeProvider>
      <ChatSessionProvider>
        <GraphSelectionProvider>
          <div className="app-shell">
            <BrandBar />
            <AppBody>{children}</AppBody>
          </div>
        </GraphSelectionProvider>
      </ChatSessionProvider>
    </ViewModeProvider>
  );
}
