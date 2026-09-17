'use client';

//  InGen Studio — boot / persistence guard
//
//  Runs once per full page load, on the client, before any child effect reads the store. Saved
//  pipelines persist ACROSS reloads (autosave writes them to localStorage); this gate's only job is
//  a one-time migration: if the stored data version differs from the code's DATA_VERSION, clear our
//  namespace once so we never try to load models written against an incompatible schema.

import { STORAGE_NAMESPACE, DATA_VERSION } from '../models/constants.js';

const NS = STORAGE_NAMESPACE;
const VERSION_KEY = `${NS}:version`;

let booted = false;

function migrateIfStale() {
  if (localStorage.getItem(VERSION_KEY) === DATA_VERSION) return; // up to date — keep saved work

  const oldVersion = localStorage.getItem(VERSION_KEY) ?? 'none';
  const staleKeys = Object.keys(localStorage).filter((k) => k.startsWith(NS + ':'));

  // Snapshot old data into a backup key before wiping so a future recovery path is possible.
  if (staleKeys.length > 0) {
    const backup = {};
    staleKeys.forEach((k) => { backup[k] = localStorage.getItem(k); });
    try {
      localStorage.setItem(`${NS}:backup:${oldVersion}`, JSON.stringify(backup));
    } catch {
      // Storage full — skip backup silently, still need to migrate.
    }
    console.warn(
      `[InGen] Data schema changed (${oldVersion} → ${DATA_VERSION}). ` +
      `${staleKeys.length} key(s) cleared. Backup saved to "${NS}:backup:${oldVersion}".`
    );
  }

  staleKeys.forEach((k) => localStorage.removeItem(k));
  localStorage.setItem(VERSION_KEY, DATA_VERSION);
}

export default function BootGate({ children }) {
  // localStorage is client-only; guard so this is inert during server rendering.
  if (typeof window !== 'undefined' && !booted) {
    booted = true;
    migrateIfStale();
  }
  return children;
}
