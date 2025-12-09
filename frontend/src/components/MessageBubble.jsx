import { User, Bot, AlertCircle } from 'lucide-react';
import clsx from 'clsx';
import ReactMarkdown from 'react-markdown';
import SourcesPanel from './SourcesPanel';
import ThinkingIndicator from './ThinkingIndicator';

/**
 * Message bubble component with different styles for user/assistant/error
 */
export default function MessageBubble({ message }) {
  const isUser = message.type === 'user';
  const isError = message.type === 'error';
  const isAssistant = message.type === 'assistant';

  return (
    <div
      className={clsx(
        'flex items-start space-x-3 animate-fadeIn',
        isUser && 'flex-row-reverse space-x-reverse'
      )}
    >
      {/* Avatar */}
      <div
        className={clsx(
          'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center shadow-lg',
          isUser && 'bg-gradient-to-br from-gray-600 to-gray-700',
          isAssistant && 'bg-gradient-to-br from-primary-500 to-secondary-500',
          isError && 'bg-gradient-to-br from-red-500 to-orange-500'
        )}
      >
        {isUser && <User className="w-6 h-6 text-white" />}
        {isAssistant && <Bot className="w-6 h-6 text-white" />}
        {isError && <AlertCircle className="w-6 h-6 text-white" />}
      </div>

      {/* Message content */}
      <div
        className={clsx(
          'flex-1 max-w-3xl',
          isUser && 'flex justify-end'
        )}
      >
        <div
          className={clsx(
            'rounded-2xl p-4 shadow-sm',
            isUser && 'bg-gradient-to-br from-gray-700 to-gray-800 text-white',
            isAssistant && 'bg-gradient-to-br from-white to-gray-50 border border-gray-200',
            isError && 'bg-red-50 border border-red-200'
          )}
        >
          {/* LLM Provider badge */}
          {isAssistant && message.llmProvider && (
            <div className="flex items-center space-x-2 mb-2">
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-primary-100 to-secondary-100 text-primary-700 border border-primary-200">
                {message.llmProvider === 'qwen' ? '🤖 Qwen' : '✨ Gemini'}
              </span>
              {message.isStreaming && (
                <span className="inline-flex items-center space-x-1">
                  <span className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></span>
                  <span className="text-xs text-primary-600">Streaming...</span>
                </span>
              )}
            </div>
          )}

          {/* Thinking indicator for streaming messages */}
          {isAssistant && message.thinking && message.thinking.length > 0 && (
            <ThinkingIndicator steps={message.thinking} />
          )}

          {/* Message text */}
          <div
            className={clsx(
              'prose prose-sm max-w-none',
              isUser && 'text-white prose-invert',
              isAssistant && 'text-gray-800',
              isError && 'text-red-800'
            )}
          >
            {isAssistant ? (
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p className="mb-2 leading-relaxed">{children}</p>,
                  strong: ({ children }) => <strong className="font-semibold text-primary-700">{children}</strong>,
                  ul: ({ children }) => <ul className="list-disc list-inside space-y-1">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal list-inside space-y-1">{children}</ol>,
                  code: ({ children }) => (
                    <code className="px-1.5 py-0.5 bg-gray-100 border border-gray-200 rounded text-sm font-mono">
                      {children}
                    </code>
                  ),
                }}
              >
                {message.content || (message.isStreaming ? '' : 'Thinking...')}
              </ReactMarkdown>
            ) : (
              <p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>
            )}
          </div>

          {/* Sources panel for assistant messages */}
          {isAssistant && message.sources && message.sources.length > 0 && (
            <SourcesPanel sources={message.sources} />
          )}

          {/* Timestamp */}
          <div
            className={clsx(
              'mt-2 text-xs',
              isUser && 'text-gray-300',
              (isAssistant || isError) && 'text-gray-500'
            )}
          >
            {new Date(message.timestamp).toLocaleTimeString('vi-VN', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
