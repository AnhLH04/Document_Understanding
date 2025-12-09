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
   * Send a query to the chat endpoint
   * @param {string} query - User's question
   * @param {string} llmProvider - 'qwen' or 'gemini'
   * @returns {Promise<Object>} Chat response with answer and sources
   */
  async sendQuery(query, llmProvider = 'qwen') {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          llm_provider: llmProvider,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new APIError(
          data.message || 'Failed to get response',
          response.status,
          data.detail
        );
      }

      return data;
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
