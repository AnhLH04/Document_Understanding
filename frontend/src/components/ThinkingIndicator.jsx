import { CheckCircle2, Loader2 } from 'lucide-react';

/**
 * Thinking indicator that displays real-time status steps
 */
export default function ThinkingIndicator({ steps = [] }) {
  return (
    <div className="mb-4 p-3 bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg">
      <div className="space-y-2">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center space-x-2 text-sm">
            <CheckCircle2 className="w-4 h-4 text-primary-500 flex-shrink-0" />
            <span className="text-gray-700">{step}</span>
          </div>
        ))}
        {steps.length > 0 && (
          <div className="flex items-center space-x-2 text-sm">
            <Loader2 className="w-4 h-4 text-primary-500 animate-spin flex-shrink-0" />
            <span className="text-gray-600">Đang tạo câu trả lời...</span>
          </div>
        )}
      </div>
    </div>
  );
}
