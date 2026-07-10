import type { 
  SupportedLanguage, 
  YouTubeQuestion, 
  YouTubeQuestionType, 
  SummarizeLevel, 
  RewriteTone,
  AIToolSSEChunk,
  YouTubeInfo
} from '@/models/ai'
import { PaymentRequiredError, TooManyRequestsError } from '@/utils/aiApiError'

const uuidv4 = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

export const SUPPORTED_LANGUAGES: SupportedLanguage[] = [
  { code: 'vi', name: 'Vietnamese', native_name: 'Tiếng Việt' },
  { code: 'en', name: 'English', native_name: 'English' },
  { code: 'zh', name: 'Chinese', native_name: '中文' },
  { code: 'ja', name: 'Japanese', native_name: '日本語' },
  { code: 'ko', name: 'Korean', native_name: '한국어' },
  { code: 'fr', name: 'French', native_name: 'Français' },
  { code: 'de', name: 'German', native_name: 'Deutsch' },
  { code: 'es', name: 'Spanish', native_name: 'Español' },
  { code: 'pt', name: 'Portuguese', native_name: 'Português' },
  { code: 'ru', name: 'Russian', native_name: 'Русский' },
  { code: 'th', name: 'Thai', native_name: 'ไทย' },
  { code: 'id', name: 'Indonesian', native_name: 'Bahasa Indonesia' },
  { code: 'ms', name: 'Malay', native_name: 'Bahasa Melayu' },
  { code: 'it', name: 'Italian', native_name: 'Italiano' },
  { code: 'ar', name: 'Arabic', native_name: 'العربية' },
  { code: 'hi', name: 'Hindi', native_name: 'हिन्दी' },
  { code: 'nl', name: 'Dutch', native_name: 'Nederlands' },
  { code: 'pl', name: 'Polish', native_name: 'Polski' },
  { code: 'tr', name: 'Turkish', native_name: 'Türkçe' },
  { code: 'sv', name: 'Swedish', native_name: 'Svenska' }
]

// Hàm tiện ích tạo delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// 1. Summarizer Mock
export async function* streamMockSummarize(text: string, level: SummarizeLevel): AsyncGenerator<AIToolSSEChunk, void, unknown> {
  // Simulate billing/rate-limit errors from Service layer (không để trong ViewModel)
  if (text === '402') throw new PaymentRequiredError()
  if (text === '429') throw new TooManyRequestsError(10)

  await delay(500)

  const summary = level === 'short'
    ? 'Đây là bản tóm tắt ngắn gọn.\n- Ý chính 1\n- Ý chính 2'
    : level === 'detailed'
      ? 'Đây là bản tóm tắt chi tiết.\n- Luận điểm 1: Rất dài và chi tiết.\n- Luận điểm 2: Có nhiều số liệu cụ thể.\n- Kết luận quan trọng.'
      : 'Đây là bản tóm tắt trung bình.\n- Điểm nổi bật 1\n- Điểm nổi bật 2\n- Tổng kết'

  const tokens = summary.split(/(?<=\s)|(?=[.,;!?:])/)
  for (let i = 0; i < tokens.length; i++) {
    await delay(30 + Math.random() * 50)
    yield {
      chunk: tokens[i],
      is_final: i === tokens.length - 1
    }
  }
}

// 2. Translator Mock
export async function* streamMockTranslate(text: string, _sourceLang: string, targetLang: string): AsyncGenerator<AIToolSSEChunk, void, unknown> {
  if (text === '402') throw new PaymentRequiredError()
  if (text === '429') throw new TooManyRequestsError(10)

  await delay(500)
  
  const targetName = SUPPORTED_LANGUAGES.find(l => l.code === targetLang)?.native_name || targetLang
  const translation = `Đây là bản dịch mô phỏng sang ngôn ngữ ${targetName} cho đoạn văn: "${text.substring(0, 30)}..."`

  const tokens = translation.split(/(?<=\s)|(?=[.,;!?:])/)
  for (let i = 0; i < tokens.length; i++) {
    await delay(20 + Math.random() * 40)
    yield {
      chunk: tokens[i],
      is_final: i === tokens.length - 1
    }
  }
}

// 3. Rewriter Mock
export async function* streamMockRewrite(text: string, tone: RewriteTone): AsyncGenerator<AIToolSSEChunk, void, unknown> {
  if (text === '402') throw new PaymentRequiredError()
  if (text === '429') throw new TooManyRequestsError(10)

  await delay(500)
  
  let prefix = ''
  switch (tone) {
    case 'formal': prefix = 'Kính thưa quý vị, sau đây là nội dung đã được tinh chỉnh: '; break;
    case 'friendly': prefix = 'Chào bạn! Mình đã viết lại đoạn này cho tự nhiên hơn nè: '; break;
    case 'concise': prefix = 'Tóm lại: '; break;
    case 'academic': prefix = 'Theo quan điểm học thuật, vấn đề này có thể được diễn giải như sau: '; break;
    case 'creative': prefix = 'Vút bay cùng ý tưởng mới: '; break;
  }
  
  const rewritten = `${prefix}${text.substring(0, 50)}... (Đã viết lại hoàn chỉnh)`

  const tokens = rewritten.split(/(?<=\s)|(?=[.,;!?:])/)
  for (let i = 0; i < tokens.length; i++) {
    await delay(30 + Math.random() * 50)
    yield {
      chunk: tokens[i],
      is_final: i === tokens.length - 1
    }
  }
}

// 4. YouTube QA Mock

export async function extractMockYouTubeInfo(url: string): Promise<YouTubeInfo> {
  await delay(1000)
  
  let videoId = 'dQw4w9WgXcQ'
  try {
    if (url.includes('v=')) {
      videoId = url.split('v=')[1].split('&')[0]
    } else if (url.includes('youtu.be/')) {
      videoId = url.split('youtu.be/')[1].split('?')[0]
    }
  } catch (e) {
    // Log để dễ debug khi swap sang real API (không silent swallow)
    console.error('[extractMockYouTubeInfo] Failed to parse videoId from URL:', e)
  }

  return {
    title: 'Sample Video Title (Mocked extracted from URL)',
    duration: '10:05',
    thumbnail_url: `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`
  }
}

export async function getMockYouTubeQuestions(url: string, count: number, type: YouTubeQuestionType): Promise<{ status: string, data: YouTubeQuestion[] }> {
  // Simulate billing/rate-limit errors from Service layer
  if (url.includes('402')) throw new PaymentRequiredError()
  if (url.includes('429')) throw new TooManyRequestsError(10)

  await delay(2000)
  
  const questions: YouTubeQuestion[] = []
  
  for (let i = 0; i < count; i++) {
    const isMcq = type === 'mcq' || (type === 'mix' && i % 2 === 0)
    
    if (isMcq) {
      questions.push({
        id: uuidv4(),
        timestamp: `0${Math.floor(Math.random() * 9)}:${Math.floor(Math.random() * 5)}${Math.floor(Math.random() * 9)}`,
        timestamp_seconds: Math.floor(Math.random() * 500),
        question_text: `Câu hỏi trắc nghiệm số ${i + 1} được trích xuất từ video?`,
        type: 'mcq',
        options: ['Lựa chọn A', 'Lựa chọn B', 'Lựa chọn C', 'Lựa chọn D'],
        correct_answer: 'Lựa chọn B'
      })
    } else {
      questions.push({
        id: uuidv4(),
        timestamp: `0${Math.floor(Math.random() * 9)}:${Math.floor(Math.random() * 5)}${Math.floor(Math.random() * 9)}`,
        timestamp_seconds: Math.floor(Math.random() * 500),
        question_text: `Hãy phân tích điểm nổi bật được nhắc đến ở phút này? (Câu hỏi tự luận số ${i + 1})`,
        type: 'open',
        correct_answer: 'Đây là gợi ý câu trả lời. Trong video, tác giả đã nhấn mạnh...'
      })
    }
  }

  return { status: 'success', data: questions }
}
