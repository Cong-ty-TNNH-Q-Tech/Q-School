export interface ChatSession {
  id: string;
  user_id: string;
  document_id?: string;
  title: string;
  ai_persona?: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  sender_type: 'user' | 'ai';
  content: string;
  created_at: string;
}

export interface SSEChunk {
  chunk: string;
  is_final: boolean;
}
