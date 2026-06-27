import { Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ChatMessage } from '@/models/chat';

interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

export default function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const isAI = message.sender_type === 'ai';
  
  // Hiển thị animation 3 dấu chấm nếu AI đang trả lời nhưng chưa có content
  const showLoading = isAI && isStreaming && !message.content;

  return (
    <div className={cn("flex w-full mb-6", isAI ? "justify-start" : "justify-end")}>
      {isAI && (
        <div className="flex-shrink-0 mr-4 mt-1">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20">
            <Bot className="w-5 h-5 text-primary" />
          </div>
        </div>
      )}
      
      <div 
        className={cn(
          "max-w-[80%] rounded-2xl px-5 py-3.5 text-[15px] leading-relaxed shadow-sm",
          isAI 
            ? "bg-white border border-gray-100 text-gray-800" 
            : "bg-primary text-white rounded-br-sm"
        )}
      >
        {showLoading ? (
          <div className="flex space-x-1.5 h-6 items-center px-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          </div>
        ) : (
          <div className="whitespace-pre-wrap format-markdown">
            {formatMessage(message.content)}
          </div>
        )}
      </div>

      {!isAI && (
        <div className="flex-shrink-0 ml-4 mt-1 hidden">
          <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
            <User className="w-5 h-5 text-gray-500" />
          </div>
        </div>
      )}
    </div>
  );
}

// Simple markdown formatter for bold, code, quotes
function formatMessage(text: string) {
  if (!text) return null;
  
  // Tạm thời render text thuần. 
  // Để hỗ trợ markdown tốt nhất, dự án nên dùng thư viện react-markdown
  return text.split('\n').map((line, i) => {
    // Xử lý line blockquote
    if (line.startsWith('> ')) {
      return (
        <blockquote key={i} className="border-l-4 border-primary/30 pl-4 py-1 my-2 bg-primary/5 text-gray-700 italic rounded-r-md">
          {renderInlineMarkdown(line.substring(2))}
        </blockquote>
      );
    }
    
    // Xử lý dòng trống
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
  // Regex cơ bản để bôi đậm **text** và code block `code`
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
