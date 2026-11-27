//  InGen Studio — Chat History Service
//
//  Persists chat conversations per-interface in localStorage. Each interface can have multiple
//  sessions; the active session is always the most recent. Provides CRUD for the sidebar
//  history panel in Chat mode.

import { makeId } from '../utils/id.js';

const STORAGE_KEY = 'ingen_chat_history';

function readAll() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
  } catch {
    return {};
  }
}

function writeAll(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

/**
 * Get all sessions for an interface, sorted newest-first.
 * @param {string} interfaceName
 * @returns {{ id: string, messages: object[], createdAt: string, preview: string }[]}
 */
export function getSessions(interfaceName) {
  const all = readAll();
  const sessions = all[interfaceName] ?? [];
  return sessions.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
}

/**
 * Get the most recent (active) session for an interface, or null.
 * @param {string} interfaceName
 * @returns {{ id: string, messages: object[], createdAt: string, preview: string } | null}
 */
export function getActiveSession(interfaceName) {
  const sessions = getSessions(interfaceName);
  return sessions.length > 0 ? sessions[0] : null;
}

/**
 * Save or update a session. If the session id already exists it is replaced;
 * otherwise it is appended.
 * @param {string} interfaceName
 * @param {{ id: string, messages: object[], createdAt: string }} session
 */
export function saveSession(interfaceName, session) {
  const all = readAll();
  const sessions = all[interfaceName] ?? [];
  const idx = sessions.findIndex((s) => s.id === session.id);
  const preview = session.messages
    .filter((m) => m.sender === 'user')
    .map((m) => m.text)
    .slice(-1)[0] || 'Empty conversation';

  // Preserve the original creation time on update. Autosave passes a fresh timestamp on every
  // keystroke-triggered save, and getSessions() sorts on createdAt — letting it drift would
  // reshuffle the sidebar while the user types.
  const entry = {
    ...session,
    createdAt: idx >= 0 ? (sessions[idx].createdAt ?? session.createdAt) : session.createdAt,
    preview: preview.slice(0, 80),
  };

  if (idx >= 0) {
    sessions[idx] = entry;
  } else {
    sessions.push(entry);
  }

  all[interfaceName] = sessions;
  writeAll(all);
}

/**
 * Delete a specific session.
 * @param {string} interfaceName
 * @param {string} sessionId
 */
export function deleteSession(interfaceName, sessionId) {
  const all = readAll();
  all[interfaceName] = (all[interfaceName] ?? []).filter((s) => s.id !== sessionId);
  writeAll(all);
}

/**
 * Create a new empty session and return it.
 * @returns {{ id: string, messages: object[], createdAt: string, preview: string }}
 */
export function createSession() {
  const session = {
    id: makeId('chat'),
    messages: [],
    createdAt: new Date().toISOString(),
    preview: 'New conversation',
  };
  return session;
}
