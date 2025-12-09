import { MessageSquare, Sparkles } from 'lucide-react';

/**
 * Header component with gradient background
 */
export default function Header() {
  return (
    <header className="bg-gradient-to-r from-primary-600 via-primary-500 to-secondary-500 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <MessageSquare className="w-8 h-8" />
              <Sparkles className="w-4 h-4 absolute -top-1 -right-1 text-yellow-300 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Document Understanding</h1>
              <p className="text-sm text-primary-100">AI-Powered Chat Assistant</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">Online</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
