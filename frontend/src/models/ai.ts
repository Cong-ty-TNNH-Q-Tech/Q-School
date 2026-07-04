/**
 * AI Workspace TypeScript Models
 * Bao gồm: Chat, Document, AITask, GeneratedAsset
 */

export type AISenderType = 'user' | 'ai'
export type AIPersona = 'Raina' | 'Tutor' | 'StudyBot'
export type DocumentStatus = 'pending' | 'parsing' | 'ready' | 'error'
export type AITaskStatus = 'pending' | 'processing' | 'completed' | 'failed'
export type GeneratedAssetType =
  | 'email'
  | 'iep'
  | 'behavior_intervention'
  | 'report_comment'
  | 'lesson_plan'
  | 'quiz'

// ──────────────────────────────────────────────
// Chat
// ──────────────────────────────────────────────
export interface ChatMessage {
  id: string
  session_id: string
  sender_type: AISenderType
  content: string
  created_at: string
}

export interface ChatSession {
  id: string
  user_id: string
  document_id: string | null
  title: string | null
  ai_persona: AIPersona | null
  created_at: string
  last_message?: ChatMessage
}

export interface SendMessageRequest {
  content: string
  session_id?: string          // null = tạo session mới
  document_id?: string         // Kích hoạt RAG mode
  ai_persona?: AIPersona
}

// SSE stream event
export interface SSEStreamEvent {
  type: 'token' | 'done' | 'error'
  content?: string
  session_id?: string
  message_id?: string
}

// ──────────────────────────────────────────────
// Document (RAG)
// ──────────────────────────────────────────────
export interface Document {
  id: string
  uploader_id: string
  filename: string
  file_type: 'pdf' | 'docx' | 'image'
  s3_url: string
  is_public: boolean
  status: DocumentStatus
  created_at: string
}

// ──────────────────────────────────────────────
// AI Task (Background Job)
// ──────────────────────────────────────────────
export interface AITask {
  id: string
  user_id: string
  task_type: string
  status: AITaskStatus
  result_payload: Record<string, unknown> | null
  created_at: string
  completed_at: string | null
}

// ──────────────────────────────────────────────
// Generated Assets
// ──────────────────────────────────────────────
export interface GeneratedAsset {
  id: string
  creator_id: string
  asset_type: GeneratedAssetType
  input_params: Record<string, unknown> | null
  output_content: Record<string, unknown> | null
  created_at: string
}

// ──────────────────────────────────────────────
// AI Tools Hub
// ──────────────────────────────────────────────
export type AIToolType = 'summarize' | 'translate' | 'rewrite' | 'youtube-qa'
export type SummarizeLevel = 'short' | 'medium' | 'detailed'
export type RewriteTone = 'formal' | 'friendly' | 'concise' | 'academic' | 'creative'
export type YouTubeQuestionType = 'mcq' | 'open' | 'mix'

export interface SupportedLanguage {
  code: string
  name: string
  native_name: string
}

export interface SummarizeRequest {
  text: string
  level: SummarizeLevel
}

export interface TranslateRequest {
  text: string
  source_lang: string
  target_lang: string
}

export interface RewriteRequest {
  text: string
  tone: RewriteTone
}

export interface YouTubeQARequest {
  url: string
  question_count: number
  question_type: YouTubeQuestionType
}

export interface YouTubeQuestion {
  id: string
  timestamp: string
  timestamp_seconds: number
  question_text: string
  type: 'mcq' | 'open'
  options?: string[]
  correct_answer?: string
}

export interface AIToolSSEChunk {
  chunk: string
  is_final: boolean
}
