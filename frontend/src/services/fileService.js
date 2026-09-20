//  inFlow/inChat — file upload service. Talks directly to the local FastAPI wrapper (local-only
//  app, no adapter indirection needed for this). Returns { file_path, columns, preview, cached }.
//
//  TODO: Route uploads through a mode-specific adapter so mock mode can simulate file uploads
//  without requiring a running backend.

const API = process.env.NEXT_PUBLIC_API_BASE_URL || '';

function requireBackend() {
  if (!API) {
    throw new Error(
      'File operations require a running backend (NEXT_PUBLIC_API_BASE_URL is not set). ' +
      'These actions are unavailable in mock/no-server mode.'
    );
  }
}

export async function uploadFile(file) {
  requireBackend();
  const body = new FormData();
  body.append('file', file);
  const res = await fetch(`${API}/api/files/upload`, { method: 'POST', body });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Upload failed (${res.status})`);
  }
  return res.json();
}

//  Read a configured source's column names (first row) via the backend — works for file paths,
//  MySQL queries, and API endpoints. Returns string[]. Throws with the backend's message on failure.
export async function fetchSourceColumns(source) {
  requireBackend();
  const res = await fetch(`${API}/api/sources/columns`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Couldn't read columns (${res.status})`);
  }
  const { columns } = await res.json();
  return columns || [];
}

