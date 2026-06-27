import { useEffect, useRef } from 'react';
import { Bot, ArrowRight, Sparkles } from 'lucide-react';
import { useChat } from '@/viewmodels/useChat';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';

export default function ChatPage() {
  const { 
    activeMessages, 
    isStreaming, 
    sendMessage 
  } = useChat();
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeMessages, isStreaming]);

  const suggestions = [
    "Giải thích phương pháp Lớp học đảo ngược",
    "Tạo trò chơi phá băng",
    "Gợi ý đề bài kiểm tra 15p",
    "Tóm tắt bài học Pythagoras"
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-theme(spacing.16))] w-full bg-slate-50/50">
      <div className="flex-1 overflow-y-auto w-full">
        <div className="max-w-4xl mx-auto px-6 py-8 pb-32">
          
          {/* Welcome Screen (Trạng thái rỗng) */}
          {activeMessages.length === 0 && (
            <div className="flex flex-col items-center justify-center mt-20 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center shadow-lg mb-6 shadow-primary/20">
                <Bot className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-3xl font-semibold text-gray-900 mb-2 tracking-tight">Xin chào, tôi là Raina</h1>
              <p className="text-gray-500 text-lg mb-12">Trợ lý AI của bạn. Tôi có thể giúp gì cho bạn hôm nay?</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-3xl">
                {suggestions.map((text, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(text)}
                    disabled={isStreaming}
                    className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-xl hover:border-primary/50 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 group text-left disabled:opacity-50"
                  >
                    <span className="text-gray-700 font-medium text-[15px]">{text}</span>
                    <ArrowRight className="w-4 h-4 text-gray-300 group-hover:text-primary transition-colors" />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Message History */}
          <div className="flex flex-col space-y-2">
            {activeMessages.map((msg, idx) => {
              const isLastMsg = idx === activeMessages.length - 1;
              return (
                <MessageBubble 
                  key={msg.id} 
                  message={msg} 
                  isStreaming={isLastMsg && isStreaming} 
                />
              );
            })}
            <div ref={messagesEndRef} className="h-4" />
          </div>

        </div>
      </div>

      {/* Input Area (Cố định ở dưới) */}
      <div className="fixed bottom-0 left-0 right-0 lg:left-64 bg-gradient-to-t from-slate-50 via-slate-50 to-transparent pt-6 pb-6 px-4">
        <div className="max-w-4xl mx-auto">
          <ChatInput onSendMessage={sendMessage} isStreaming={isStreaming} />
          
          <div className="text-center mt-3 flex items-center justify-center text-xs text-gray-400">
            <Sparkles className="w-3 h-3 mr-1" />
            <span>Raina có thể mắc lỗi. Hãy kiểm tra lại thông tin quan trọng.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
