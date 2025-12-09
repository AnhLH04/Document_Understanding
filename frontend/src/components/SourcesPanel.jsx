import { useState } from 'react';
import { ChevronDown, ChevronUp, FileText, ExternalLink } from 'lucide-react';
import clsx from 'clsx';

/**
 * Collapsible panel showing source documents
 */
export default function SourcesPanel({ sources }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 border-t border-gray-200 pt-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full text-left group hover:bg-gray-50 rounded-lg p-2 transition-colors"
      >
        <div className="flex items-center space-x-2">
          <FileText className="w-4 h-4 text-primary-500" />
          <span className="text-sm font-medium text-gray-700">
            Nguồn tham khảo ({sources.length})
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-500 group-hover:text-gray-700" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-500 group-hover:text-gray-700" />
        )}
      </button>

      <div
        className={clsx(
          'overflow-hidden transition-all duration-300',
          isExpanded ? 'max-h-96 mt-3' : 'max-h-0'
        )}
      >
        <div className="space-y-2 overflow-y-auto max-h-80">
          {sources.map((source, index) => (
            <div
              key={index}
              className="bg-gradient-to-br from-primary-50 to-secondary-50 border border-primary-100 rounded-lg p-3 hover:shadow-md transition-shadow group"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                    {index + 1}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-800">
                      {source.filename}
                    </p>
                    <p className="text-xs text-gray-500">Trang {source.page}</p>
                  </div>
                </div>
                <ExternalLink className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              
              <p className="text-sm text-gray-600 leading-relaxed line-clamp-3">
                {source.content_preview}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
