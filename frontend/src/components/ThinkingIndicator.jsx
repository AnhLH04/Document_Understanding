import { Loader2, Brain } from 'lucide-react';

/**
 * Thinking indicator with animated brain icon
 */
export default function ThinkingIndicator() {
  return (
    <div className="flex items-start space-x-3 animate-fadeIn">
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center shadow-lg">
        <Brain className="w-6 h-6 text-white" />
      </div>
      
      <div className="flex-1 bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-2xl p-4 shadow-sm">
        <div className="flex items-center space-x-2 text-gray-600">
          <Loader2 className="w-5 h-5 animate-spin text-primary-500" />
          <span className="font-medium">AI đang suy nghĩ...</span>
        </div>
        
        <div className="mt-3 space-y-2">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-pulse"></div>
            <span>Đang tìm kiếm tài liệu liên quan</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="w-1.5 h-1.5 bg-secondary-400 rounded-full animate-pulse delay-75"></div>
            <span>Đang phân tích thông tin</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="w-1.5 h-1.5 bg-primary-400 rounded-full animate-pulse delay-150"></div>
            <span>Đang tạo câu trả lời</span>
          </div>
        </div>
        
        {/* Animated progress bar */}
        <div className="mt-3 h-1 bg-gray-200 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-primary-500 to-secondary-500 animate-gradient rounded-full" 
               style={{ width: '100%' }}></div>
        </div>
      </div>
    </div>
  );
}
