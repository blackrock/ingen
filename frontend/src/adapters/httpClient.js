//  InGen Studio — HTTP client
//
//  Thin fetch wrapper shared by the Http* adapters. Base URL comes from NEXT_PUBLIC_API_BASE_URL
//  (defaults to the local FastAPI wrapper). Surfaces the backend's `detail` message on errors.

const DEFAULT_BASE = '';

export class HttpClient {
  constructor(baseUrl) {
    this.baseUrl = (baseUrl != null && baseUrl !== '' ? baseUrl : DEFAULT_BASE).replace(/\/$/, '');
  }

  async request(method, path, body) {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) {
      let detail;
      try { detail = (await res.json())?.detail; } catch { /* non-JSON error body */ }
      throw new Error(`HTTP ${res.status} on ${path}${detail ? `: ${detail}` : ''}`);
    }
    if (res.status === 204) return null;
    return res.json();
  }

  get(path) { return this.request('GET', path); }
  post(path, body) { return this.request('POST', path, body); }
}
