/**
 * API Service for communicating with Document Understanding backend
 */

const API_BASE_URL = '/api/v1';

export class APIError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.detail = detail;
  }
}

export const chatService = {
  /**
   * Send a query to the chat endpoint with streaming support
   * @param {string} query - User's question
   * @param {string} llmProvider - 'qwen' or 'gemini'
   * @param {Object} callbacks - Callback functions for streaming events
   * @param {Function} callbacks.onStatus - Called with status messages
   * @param {Function} callbacks.onSources - Called with retrieved sources
   * @param {Function} callbacks.onText - Called with each text chunk
   * @param {Function} callbacks.onDone - Called when streaming completes
   * @param {Function} callbacks.onError - Called on error
   */
  async sendQueryStream(query, llmProvider = 'qwen', callbacks = {}) {
    const { onStatus, onSources, onText, onDone, onError } = callbacks;

    try {
      const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          llm_provider: llmProvider,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new APIError(
          data.message || 'Failed to get response',
          response.status,
          data.detail
        );
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Keep the last incomplete line in the buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6).trim();
            if (!jsonStr) continue;

            try {
              const event = JSON.parse(jsonStr);
              
              switch (event.type) {
                case 'status':
                  onStatus?.(event.data);
                  break;
                case 'sources':
                  onSources?.(event.data);
                  break;
                case 'text':
                  onText?.(event.data);
                  break;
                case 'done':
                  onDone?.(event.data);
                  return;
                case 'error':
                  onError?.(event.data);
                  return;
              }
            } catch (parseError) {
              console.error('Failed to parse SSE event:', parseError);
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(
        error.message || 'Network error',
        0,
        'Failed to connect to server'
      );
    }
  },

  /**
   * Check API health
   */
  async healthCheck() {
    try {
      const response = await fetch('/health');
      return response.ok;
    } catch {
      return false;
    }
  },
};

export default chatService;
