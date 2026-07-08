import { useState, useEffect, useRef, useMemo } from 'react';
import { Copy, Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface SSEResultDisplayProps {
  result: string;
  isStreaming: boolean;
  onCopy?: () => Promise<boolean>;
}

export function SSEResultDisplay({ result, isStreaming, onCopy }: SSEResultDisplayProps) {
  // [FIX #2] Dùng named import useState thay vì React.useState — theo convention dự án
  const [copied, setCopied] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  // [FIX #5] Lưu timeout ID để cleanup khi unmount tránh setState trên unmounted component
  const copyTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const formattedContent = useMemo(() => formatMessage(result), [result]);

  // Auto-scroll to bottom while streaming
  useEffect(() => {
    if (isStreaming && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [result, isStreaming]);

  // [FIX #5] Cleanup timeout khi unmount
  useEffect(() => {
    return () => {
      if (copyTimeoutRef.current) clearTimeout(copyTimeoutRef.current);
    };
  }, []);

  const handleCopy = async () => {
    let success = false;

    if (onCopy) {
      success = await onCopy();
    } else {
      try {
        await navigator.clipboard.writeText(result);
        success = true;
      } catch (e) {
        console.error('Failed to copy to clipboard:', e);
      }
    }

    if (success) {
      // [FIX #5] Clear trước khi set để tránh race condition double-click
      if (copyTimeoutRef.current) clearTimeout(copyTimeoutRef.current);
      setCopied(true);
      copyTimeoutRef.current = setTimeout(() => setCopied(false), 2000);
    }
  };

  const showLoading = isStreaming && !result;

  return (
    <div className="relative rounded-lg border border-gray-200 bg-gray-50/50 flex flex-col h-full min-h-[250px] overflow-hidden">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <span className="text-sm font-medium text-gray-600">Kết quả</span>
        <Button
          variant="ghost"
          size="sm"
          className="h-8 px-3 text-gray-500 hover:text-primary transition-colors"
          onClick={handleCopy}
          disabled={!result || isStreaming}
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-500" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
          <span className={cn("ml-2 text-xs", copied && "text-green-600")}>
            {copied ? 'Đã sao chép' : 'Sao chép'}
          </span>
        </Button>
      </div>

      {/* Content Area */}
      <div
        ref={scrollRef}
        className="flex-1 p-5 overflow-y-auto scroll-smooth"
      >
        {showLoading ? (
          <div className="flex space-x-1.5 h-6 items-center px-1">
            <div className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
            <div className="w-2 h-2 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
            <div className="w-2 h-2 bg-primary/40 rounded-full animate-bounce"></div>
          </div>
        ) : !result && !isStreaming ? (
          <div className="flex items-center justify-center h-full text-gray-400 text-sm italic">
            Kết quả sẽ hiển thị tại đây...
          </div>
        ) : (
          // [FIX Phase6-B4] aria-live chỉ bao quanh text kết quả thực — không bao loading/placeholder
          <div
            className="text-[15px] leading-relaxed text-gray-800 whitespace-pre-wrap"
            aria-live="polite"
            aria-atomic="false"
            aria-label="Kết quả xử lý"
          >
            {formattedContent}
            {isStreaming && (
              <span className="inline-block w-1.5 h-4 ml-1 bg-primary/80 animate-pulse align-middle" aria-hidden="true" />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Simple markdown formatter adapted from MessageBubble.tsx
function formatMessage(text: string) {
  if (!text) return null;

  return text.split('\n').map((line, i) => {
    if (line.startsWith('> ')) {
      return (
        <blockquote key={i} className="border-l-4 border-primary/30 pl-4 py-1.5 my-2 bg-primary/5 text-gray-700 italic rounded-r-md">
          {renderInlineMarkdown(line.substring(2))}
        </blockquote>
      );
    }

    if (line.match(/^[-*]\s/)) {
      return (
        <div key={i} className="flex ml-2 my-1">
          <span className="mr-2 text-primary/60">•</span>
          <span>{renderInlineMarkdown(line.substring(2))}</span>
        </div>
      );
    }

    if (line.trim() === '') {
      return <div key={i} className="h-2"></div>;
    }

    return (
      <div key={i} className="min-h-[1.5rem]">
        {renderInlineMarkdown(line)}
      </div>
    );
  });
}

function renderInlineMarkdown(text: string) {
  const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);

  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index} className="font-semibold text-gray-900">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={index} className="bg-primary/10 text-primary px-1.5 py-0.5 rounded text-sm font-mono">{part.slice(1, -1)}</code>;
    }
    return <span key={index}>{part}</span>;
  });
}
