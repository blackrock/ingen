//  HttpChatAdapter — sends messages to the real backend chat API.
//  Implements the same interface as MockChatAdapter.

/** @typedef {{ ops: object[], reply: string }} ChatResult */

export class HttpChatAdapter {
  /** @param {import('./httpClient.js').HttpClient} client */
  constructor(client) {
    this._client = client;
  }

  /**
   * @param {string} message
   * @param {string[]} columns
   * @param {string} yaml
   * @param {string} interfaceName
   * @param {{role: string, content: string}[]} history  recent turns for follow-up context
   * @returns {Promise<ChatResult>}
   */
  async interpret(message, columns = [], yaml = '', interfaceName = '', history = []) {
    const res = await fetch(`${this._client.baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, columns, yaml, interface: interfaceName, history }),
    });
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}));
      throw new Error(detail.detail || `Chat failed (${res.status})`);
    }
    const { ops, reply } = await res.json();
    return {
      ops: Array.isArray(ops) ? ops : [],
      reply: typeof reply === 'string' ? reply : '',
    };
  }

  /** Fire-and-forget warmup to pre-load the model on the backend. */
  warmup() {
    fetch(`${this._client.baseUrl}/api/chat/warmup`, { method: 'POST' }).catch(() => {});
  }
}
