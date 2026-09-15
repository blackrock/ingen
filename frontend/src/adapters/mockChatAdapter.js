//  MockChatAdapter — returns regex-parsed ops without network, matching the ChatService interface.
//  Used when ADAPTER_MODE is MOCK (no backend).

/** @typedef {{ ops: object[], reply: string }} ChatResult */

export class MockChatAdapter {
  /**
   * Interpret a user message as pipeline edit ops.
   * In mock mode, always throws so the caller falls back to its local regex parser.
   * Accepts the same arguments as HttpChatAdapter.interpret
   * (message, columns, yaml, interfaceName, history) but ignores all of them.
   * @returns {Promise<ChatResult>}
   */
  async interpret() {
    throw new Error('LLM unavailable (mock mode) — using regex fallback');
  }

  /** No-op in mock mode. */
  warmup() {}
}
