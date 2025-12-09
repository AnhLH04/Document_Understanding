import { useState, useCallback } from 'react';
import { chatService } from '../services/api';

/**
 * Custom hook for managing chat functionality with streaming support
 */
export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [streamingMessageId, setStreamingMessageId] = useState(null);

  const sendMessage = useCallback(async (query, llmProvider = 'qwen') => {
    if (!query.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    // Create placeholder for AI response
    const aiMessageId = Date.now() + 1;
    const aiMessage = {
      id: aiMessageId,
      type: 'assistant',
      content: '',
      sources: [],
      llmProvider: llmProvider,
      timestamp: new Date(),
      thinking: [],
      isStreaming: true,
    };

    setMessages(prev => [...prev, aiMessage]);
    setStreamingMessageId(aiMessageId);

    try {
      // Call streaming API
      await chatService.sendQueryStream(query, llmProvider, {
        onStatus: (status) => {
          // Update thinking steps
          setMessages(prev =>
            prev.map(msg =>
              msg.id === aiMessageId
                ? { ...msg, thinking: [...(msg.thinking || []), status] }
                : msg
            )
          );
        },
        onSources: (sources) => {
          // Update sources
          setMessages(prev =>
            prev.map(msg =>
              msg.id === aiMessageId
                ? { ...msg, sources }
                : msg
            )
          );
        },
        onText: (text) => {
          // Append text chunk
          setMessages(prev =>
            prev.map(msg =>
              msg.id === aiMessageId
                ? { ...msg, content: msg.content + text }
                : msg
            )
          );
        },
        onDone: (data) => {
          // Mark streaming as complete
          setMessages(prev =>
            prev.map(msg =>
              msg.id === aiMessageId
                ? { ...msg, isStreaming: false }
                : msg
            )
          );
          setIsLoading(false);
          setStreamingMessageId(null);
        },
        onError: (errorMsg) => {
          setError(errorMsg);
          
          // Update message to show error
          setMessages(prev =>
            prev.map(msg =>
              msg.id === aiMessageId
                ? { ...msg, type: 'error', content: errorMsg, isStreaming: false }
                : msg
            )
          );
          setIsLoading(false);
          setStreamingMessageId(null);
        },
      });
    } catch (err) {
      setError(err.message || 'Failed to get response');
      
      // Update message to show error
      setMessages(prev =>
        prev.map(msg =>
          msg.id === aiMessageId
            ? { ...msg, type: 'error', content: err.message || 'Failed to get response from server', isStreaming: false }
            : msg
        )
      );
      setIsLoading(false);
      setStreamingMessageId(null);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    setStreamingMessageId(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    streamingMessageId,
    sendMessage,
    clearMessages,
  };
}
