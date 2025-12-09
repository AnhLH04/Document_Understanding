import { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Loader2 } from 'lucide-react';
import MessageBubble from './MessageBubble';
import ThinkingIndicator from './ThinkingIndicator';

/**
 * Main chat container with messages and input
 */
export default function ChatContainer({ messages, isLoading, onSendMessage, onClear }) {
  const [input, setInput] = useState('');
  const [llmProvider, setLlmProvider] = useState('qwen');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input, llmProvider);
      setInput('');
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        <div className="container mx-auto max-w-5xl px-4 py-6">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-4 animate-fadeIn">
                <div className="w-20 h-20 mx-auto bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center shadow-xl">
                  <Send className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-800">
                  Chào mừng đến với Document Understanding
                </h2>
                <p className="text-gray-600 max-w-md mx-auto">
                  Hãy đặt câu hỏi về tài liệu của bạn. AI sẽ tìm kiếm và trả lời dựa trên
                  nội dung đã được index trong hệ thống.
                </p>
                <div className="flex items-center justify-center space-x-4 pt-4">
                  <div className="bg-white rounded-lg px-4 py-2 shadow-sm border border-gray-200">
                    <p className="text-sm text-gray-600">💡 Ví dụ: "Tóm tắt nội dung chính?"</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
              
              {isLoading && <ThinkingIndicator />}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input area */}
      <div className="border-t border-gray-300 bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto max-w-5xl px-4 py-4">
          <form onSubmit={handleSubmit} className="space-y-3">
            {/* LLM Provider selector */}
            <div className="flex items-center space-x-3">
              <span className="text-sm font-medium text-gray-700">Model:</span>
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={() => setLlmProvider('qwen')}
                  className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                    llmProvider === 'qwen'
                      ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-md'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  🤖 Qwen (Local)
                </button>
                <button
                  type="button"
                  onClick={() => setLlmProvider('gemini')}
                  className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                    llmProvider === 'gemini'
                      ? 'bg-gradient-to-r from-secondary-500 to-secondary-600 text-white shadow-md'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  ✨ Gemini (API)
                </button>
              </div>

              {messages.length > 0 && (
                <button
                  type="button"
                  onClick={onClear}
                  className="ml-auto flex items-center space-x-2 px-3 py-1.5 rounded-full text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Xóa lịch sử</span>
                </button>
              )}
            </div>

            {/* Input field */}
            <div className="flex items-end space-x-3">
              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Nhập câu hỏi của bạn..."
                  disabled={isLoading}
                  rows={1}
                  className="w-full px-4 py-3 pr-12 border-2 border-gray-300 rounded-2xl focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none resize-none disabled:bg-gray-100 disabled:cursor-not-allowed transition-all"
                  style={{
                    minHeight: '52px',
                    maxHeight: '150px',
                  }}
                />
              </div>
              
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 text-white rounded-full flex items-center justify-center shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-105 active:scale-95"
              >
                {isLoading ? (
                  <Loader2 className="w-6 h-6 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>

            <p className="text-xs text-gray-500 text-center">
              Nhấn Enter để gửi, Shift+Enter để xuống dòng
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
