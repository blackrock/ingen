//  InGen Studio — ChatSessionContext
//
//  Bridges the Chat-mode sidebar (NavRail, which lists every saved conversation) and the chat
//  editor (InterfaceChatEditor, which owns the live conversation). They live in different branches
//  of the tree, so this shared state is how the sidebar drives the editor:
//
//    - The editor reports its current session id via `setActiveSessionId` so the sidebar can
//      highlight the open conversation.
//    - The sidebar issues a one-shot `command` ({ kind: 'new' } | { kind: 'load', ... }); the
//      editor picks it up and calls `consumeCommand()` so it fires exactly once.

import { createContext, useContext, useState, useCallback, useMemo } from 'react';

const ChatSessionContext = createContext(null);

export function ChatSessionProvider({ children }) {
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [command, setCommand] = useState(null);

  const requestNew = useCallback(() => setCommand({ kind: 'new', nonce: Date.now() }), []);
  const requestLoad = useCallback(
    (interfaceName, sessionId) =>
      setCommand({ kind: 'load', interfaceName, sessionId, nonce: Date.now() }),
    [],
  );
  const consumeCommand = useCallback(() => setCommand(null), []);

  const value = useMemo(
    () => ({ activeSessionId, setActiveSessionId, command, requestNew, requestLoad, consumeCommand }),
    [activeSessionId, command, requestNew, requestLoad, consumeCommand],
  );

  return <ChatSessionContext.Provider value={value}>{children}</ChatSessionContext.Provider>;
}

export function useChatSession() {
  const ctx = useContext(ChatSessionContext);
  if (!ctx) throw new Error('useChatSession must be used within a ChatSessionProvider');
  return ctx;
}
