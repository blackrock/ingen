import { useState, useRef, useEffect, useCallback } from 'react';
import { Bot, User, Sparkles } from 'lucide-react';
import { useConfig } from '../../../state/ConfigContext.jsx';
import { useChatSession } from '../../../state/ChatSessionContext.jsx';
import { applyOps } from '../../../models/applyIntent.js';
import { getServices } from '../../../services/index.js';
import { columnsForSources } from '../../../lib/columnStore.js';
import { modelToYaml } from '../../../serializers/yamlSerializer.js';
import MiniMarkdown from '../../common/MiniMarkdown.jsx';
import {
  getActiveSession,
  getSessions,
  saveSession,
  createSession,
} from '../../../services/chatHistoryService.js';

function welcomeMessage(interfaceName) {
  return {
    id: 'welcome',
    sender: 'assistant',
    text: `Hi! I'm **inChat**, your pipeline assistant for **${interfaceName}**. Tell me what you want in plain language — I'll wire up sources, filters, and output for you. The suggestions below are tailored to what you've built so far.`,
  };
}

// Regex fallback — used when the local model is unavailable. Returns the SAME ops shape the backend
// produces, so a single applier handles both paths.
// Op authority: frontend/src/models/applyIntent.js — only emit ops it implements.
function regexOps(text) {
  const t = text.trim();
  let m;
  if ((m = t.match(/^add\s+columns?\s+(.+)/i))) {
    const cols = m[1].split(/[,\s]+/).map((s) => s.trim()).filter(Boolean);
    return cols.length ? [{ op: 'add_columns', cols }] : [];
  }
  if ((m = t.match(/^remove\s+columns?\s+(\S+)/i))) return [{ op: 'remove_column', name: m[1] }];
  if ((m = t.match(/^rename\s+(\w+)\s+(?:to\s+)?(\w+)/i))) return [{ op: 'rename_column', from: m[1], to: m[2] }];
  if ((m = t.match(/^add\s+source\s+(\w+)\s+(\w+)/i))) return [{ op: 'add_source', name: m[1], type: m[2].toLowerCase() }];
  if ((m = t.match(/^remove\s+source\s+(\S+)/i))) return [{ op: 'remove_source', name: m[1] }];
  if ((m = t.match(/^add\s+transform\s+(\w+)/i))) return [{ op: 'add_transform', type: m[1].toLowerCase() }];
  if ((m = t.match(/^remove\s+transform\s+(\w+)/i))) return [{ op: 'remove_transform', type: m[1].toLowerCase() }];
  if ((m = t.match(/^filter\s+(\w+)\s+(.+)/i))) return [{ op: 'add_filter', col: m[1], val: m[2] }];
  if ((m = t.match(/^change\s+output\s+to\s+(\w+)/i))) return [{ op: 'set_output', type: m[1].toLowerCase() }];
  if (/^(explain|describe|what.*(pipeline|interface))/i.test(t)) return [{ op: 'explain' }];
  return [];
}

// Suggestion chips derived from current state — always valid, never LLM-guessed.
function suggestionsFor(iface, columns) {
  const out = [];
  out.push('explain');
  if (columns.length) out.push(`add columns ${columns.slice(0, 3).join(', ')}`);
  else if ((iface?.columns?.length ?? 0) === 0) out.push('add columns id, status, amount');
  const col = columns[0] || (iface?.columns?.[0]?.src_col_name);
  if (col) out.push(`filter ${col} CLOSED`);
  if (!iface?.output?.type) out.push('change output to excel');
  return out.slice(0, 4);
}

export default function InterfaceChatEditor({ interfaceName, iface }) {
  const { model, updateModel } = useConfig();
  const { setActiveSessionId, command, consumeCommand } = useChatSession();
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const knownColumns = columnsForSources(iface?.sources ?? []);

  // Pre-warm the local model once when the chat opens, so the first message isn't slow.
  useEffect(() => { getServices().chat.warmup(); }, []);

  //  Load (or start) the conversation for whichever interface is being edited. Done during render
  //  rather than in an effect — React's "adjust state when a prop changes" pattern — so switching
  //  interfaces never paints one frame of the previous interface's messages.
  const [loadedFor, setLoadedFor] = useState(null);
  if (loadedFor !== interfaceName) {
    setLoadedFor(interfaceName);
    const active = getActiveSession(interfaceName);
    if (active && active.messages.length > 0) {
      setSessionId(active.id);
      setMessages(active.messages);
    } else {
      setSessionId(createSession().id);
      setMessages([welcomeMessage(interfaceName)]);
    }
  }

  useEffect(() => {
    if (sessionId) setActiveSessionId(sessionId);
  }, [sessionId, setActiveSessionId]);

  //  One-shot commands from the sidebar (new conversation / load conversation).
  //
  //  This genuinely has to be an effect, so the set-state-in-effect rule is suppressed below:
  //  consumeCommand() calls setCommand(null) on ChatSessionProvider, and updating another
  //  component's state during render is illegal in React ("Cannot update a component while
  //  rendering a different component"). The command is cleared on receipt, so this runs exactly
  //  once per command and cannot cascade.
  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (!command) return;
    if (command.kind === 'new') {
      setSessionId(createSession().id);
      setMessages([welcomeMessage(interfaceName)]);
      consumeCommand();
    } else if (command.kind === 'load' && command.interfaceName === interfaceName) {
      const target = getSessions(interfaceName).find((s) => s.id === command.sessionId);
      if (target) {
        setSessionId(target.id);
        setMessages(target.messages.length ? target.messages : [welcomeMessage(interfaceName)]);
      }
      consumeCommand();
    }
  }, [command, interfaceName, consumeCommand]);
  /* eslint-enable react-hooks/set-state-in-effect */

  useEffect(() => {
    if (sessionId && messages.length > 0) {
      saveSession(interfaceName, { id: sessionId, messages, createdAt: new Date().toISOString() });
    }
  }, [messages, sessionId, interfaceName]);

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  useEffect(() => { scrollToBottom(); }, [messages, isTyping]);

  const handleSendMessage = useCallback((textToSend) => {
    if (!textToSend.trim()) return;
    // Recent dialogue (before this new turn) so the model can resolve follow-ups like "now also add X".
    const history = messages
      .filter((m) => m.id !== 'welcome')
      .slice(-6)
      .map((m) => ({ role: m.sender === 'user' ? 'user' : 'assistant', content: m.text }));
    setMessages((prev) => [...prev, { id: `msg-${Date.now()}`, sender: 'user', text: textToSend }]);
    setInputValue('');
    setIsTyping(true);

    // Snapshot YAML from current model for the LLM context, then fire the request.
    const yaml = (() => { try { return modelToYaml(model); } catch { return ''; } })();
    getServices().chat.interpret(textToSend, knownColumns, yaml, interfaceName, history)
      .catch(() => ({ ops: regexOps(textToSend), reply: '' }))
      .then(({ ops, reply: modelReply }) => {
        // Apply ops inside the functional updater so they always thread through the LATEST
        // committed model — not the stale closure snapshot — preventing concurrent-message races.
        let reply = '';
        let changed = false;
        updateModel((currentModel) => {
          const result = applyOps(currentModel, interfaceName, knownColumns, ops);
          reply = result.reply;
          changed = result.changed;
          return result.model;
        });
        const isConversation = (ops?.length ?? 0) === 0;
        const text = modelReply && (changed || isConversation) ? modelReply : reply;
        setMessages((prev) => [...prev, { id: `msg-reply-${Date.now()}`, sender: 'assistant', text }]);
      })
      .catch(() => {
        setMessages((prev) => [...prev, {
          id: `msg-reply-${Date.now()}`,
          sender: 'assistant',
          text: "Sorry — I couldn't apply that change. Please try rephrasing it.",
        }]);
      })
      // Always clear the indicator: if applyOps throws above, the spinner would otherwise never stop.
      .finally(() => setIsTyping(false));
  }, [model, updateModel, interfaceName, knownColumns, messages]);

  const chips = suggestionsFor(iface, knownColumns);

  const fmtTime = (id) => {
    const ts = parseInt(id?.split('-').pop(), 10);
    if (!ts || Number.isNaN(ts)) return '';
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chateditor">
      <div className="chateditor__messages">
        {messages.map((m) => (
          <div key={m.id} className={`chatbubble chatbubble--${m.sender}`}>
            <div className={`chatbubble__avatar chatbubble__avatar--${m.sender}`} aria-hidden="true">
              {m.sender === 'user' ? <User size={14} /> : <Bot size={14} />}
            </div>
            <div className="chatbubble__body">
              {m.sender === 'assistant'
                ? <MiniMarkdown text={m.text} className="chatbubble__content chatbubble__content--assistant" />
                : <div className="chatbubble__content chatbubble__content--user">{m.text}</div>
              }
              {m.id !== 'welcome' && (
                <span className="chatbubble__time">{fmtTime(m.id)}</span>
              )}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="chatbubble chatbubble--assistant">
            <div className="chatbubble__avatar chatbubble__avatar--assistant" aria-hidden="true">
              <Bot size={14} />
            </div>
            <div className="chatbubble__body">
              <div className="chatbubble__content chatbubble__content--assistant">
                <div className="typing-indicator"><span></span><span></span><span></span></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chateditor__inputarea">
        <div className="prompt-chips">
          {chips.map((c) => (
            <button key={c} className="prompt-chip" onClick={() => handleSendMessage(c)}>
              {c === 'explain' ? <><Sparkles size={11} /> explain</> : `+ ${c}`}
            </button>
          ))}
        </div>

        <form className="chateditor__form" onSubmit={(e) => { e.preventDefault(); handleSendMessage(inputValue); }}>
          <input
            type="text"
            className="chateditor__input"
            placeholder="Describe a change to your pipeline…"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isTyping}
            autoComplete="off"
          />
          <button type="submit" className="btn btn--accent" disabled={!inputValue.trim() || isTyping} style={{ padding: '10px 20px' }}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
