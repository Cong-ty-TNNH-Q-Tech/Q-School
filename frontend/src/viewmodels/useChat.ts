import { useState, useCallback, useEffect } from 'react';
import type { ChatSession, ChatMessage } from '@/models/chat';
import { streamMockChatResponse } from '@/services/sseClient';

export function useChat() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Record<string, ChatMessage[]>>({});
  const [isStreaming, setIsStreaming] = useState(false);

  // Khởi tạo một mock session mặc định
  useEffect(() => {
    if (sessions.length === 0) {
      const defaultSessionId = 'mock-session-1';
      setSessions([{
        id: defaultSessionId,
        user_id: 'user-1',
        title: 'Trò chuyện mới',
        created_at: new Date().toISOString()
      }]);
      setActiveSessionId(defaultSessionId);
      setMessages({ [defaultSessionId]: [] });
    }
  }, [sessions.length]);

  const activeMessages = activeSessionId ? (messages[activeSessionId] || []) : [];

  const createSession = useCallback(() => {
    const newSessionId = `session-${Date.now()}`;
    const newSession: ChatSession = {
      id: newSessionId,
      user_id: 'user-1',
      title: 'Cuộc trò chuyện mới',
      created_at: new Date().toISOString()
    };
    setSessions(prev => [newSession, ...prev]);
    setMessages(prev => ({ ...prev, [newSessionId]: [] }));
    setActiveSessionId(newSessionId);
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!activeSessionId || !content.trim() || isStreaming) return;

    // Thêm tin nhắn user
    const userMsgId = `msg-${Date.now()}`;
    const userMessage: ChatMessage = {
      id: userMsgId,
      session_id: activeSessionId,
      sender_type: 'user',
      content: content.trim(),
      created_at: new Date().toISOString()
    };

    // Thêm sẵn tin nhắn AI rỗng để chuẩn bị nhận stream
    const aiMsgId = `msg-ai-${Date.now()}`;
    const aiMessage: ChatMessage = {
      id: aiMsgId,
      session_id: activeSessionId,
      sender_type: 'ai',
      content: '',
      created_at: new Date().toISOString()
    };

    setMessages(prev => {
      const sessionMsgs = prev[activeSessionId] || [];
      return {
        ...prev,
        [activeSessionId]: [...sessionMsgs, userMessage, aiMessage]
      };
    });

    setIsStreaming(true);

    try {
      // Gọi hàm nhận luồng dữ liệu (mock)
      const stream = streamMockChatResponse(content);
      
      for await (const chunk of stream) {
        setMessages(prev => {
          const sessionMsgs = prev[activeSessionId] || [];
          const updatedMsgs = [...sessionMsgs];
          const lastMsgIndex = updatedMsgs.length - 1;
          
          if (lastMsgIndex >= 0 && updatedMsgs[lastMsgIndex].id === aiMsgId) {
            updatedMsgs[lastMsgIndex] = {
              ...updatedMsgs[lastMsgIndex],
              content: updatedMsgs[lastMsgIndex].content + chunk.chunk
            };
          }
          
          return {
            ...prev,
            [activeSessionId]: updatedMsgs
          };
        });
      }
    } catch (error) {
      console.error("Lỗi khi nhận luồng chat:", error);
    } finally {
      setIsStreaming(false);
    }
  }, [activeSessionId, isStreaming]);

  return {
    sessions,
    activeSessionId,
    setActiveSessionId,
    activeMessages,
    isStreaming,
    sendMessage,
    createSession
  };
}
