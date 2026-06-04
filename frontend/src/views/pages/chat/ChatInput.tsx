import { useState, useRef, type KeyboardEvent } from 'react';
import { Paperclip, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isStreaming: boolean;
}

export default function ChatInput({ onSendMessage, isStreaming }: ChatInputProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (text.trim() && !isStreaming) {
      onSendMessage(text);
      setText('');
      // Reset height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    // Auto resize
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  return (
    <div className="relative rounded-2xl border border-gray-200 bg-white shadow-sm flex items-end p-2 focus-within:ring-1 focus-within:ring-primary/50 focus-within:border-primary transition-all">
      <Button 
        variant="ghost" 
        size="icon" 
        className="h-10 w-10 shrink-0 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-xl mr-1"
        disabled={isStreaming}
      >
        <Paperclip className="h-5 w-5" />
      </Button>
      
      <textarea
        ref={textareaRef}
        value={text}
        onChange={handleInput}
        onKeyDown={handleKeyDown}
        placeholder="Hỏi Raina về bài giảng, bài tập, hoặc bất cứ điều gì..."
        className="w-full resize-none bg-transparent border-0 focus:ring-0 text-[15px] p-2.5 max-h-[120px] outline-none disabled:opacity-50"
        rows={1}
        disabled={isStreaming}
      />
      
      <Button 
        onClick={handleSend}
        disabled={!text.trim() || isStreaming}
        size="icon"
        className="h-10 w-10 shrink-0 rounded-xl bg-primary text-white hover:bg-primary/90 ml-1 transition-colors"
      >
        <Send className="h-5 w-5" />
      </Button>
    </div>
  );
}
