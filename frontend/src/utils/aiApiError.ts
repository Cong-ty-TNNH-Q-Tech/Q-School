/**
 * AI API Error Utilities
 *
 * Định nghĩa Custom Error classes khớp với error codes trong openapi.yaml
 * (PaymentRequiredError: 4020, TooManyRequestsError: 4290).
 *
 * ViewModel tuyệt đối KHÔNG .includes() chuỗi lỗi — chỉ dùng parseAIError().
 */

// ─────────────────────────────────────────────
// Custom Error Classes
// ─────────────────────────────────────────────

/** HTTP 402 / Error Code 4020 */
export class PaymentRequiredError extends Error {
  readonly errorCode = 4020
  readonly retryAfter?: number

  constructor(message = 'Bạn đã hết lượt sử dụng. Vui lòng nâng cấp gói cước để tiếp tục.') {
    super(message)
    this.name = 'PaymentRequiredError'
  }
}

/** HTTP 429 / Error Code 4290 */
export class TooManyRequestsError extends Error {
  readonly errorCode = 4290
  readonly retryAfter: number

  constructor(retryAfter = 15, message = 'Hệ thống đang quá tải. Vui lòng thử lại sau.') {
    super(message)
    this.name = 'TooManyRequestsError'
    this.retryAfter = retryAfter
  }
}

// ─────────────────────────────────────────────
// Error Result Union Type
// ─────────────────────────────────────────────

export type AIErrorResult =
  | { type: 'payment_required' }
  | { type: 'rate_limit'; seconds: number }
  | { type: 'generic'; message: string }

// ─────────────────────────────────────────────
// Error Mapper
// ─────────────────────────────────────────────

/**
 * Maps a caught error → AIErrorResult.
 * ViewModel chỉ cần gọi hàm này và dispatch state theo type.
 * Tuân thủ OCP: khi API thay đổi error format, chỉ sửa hàm này.
 */
export function parseAIError(err: unknown): AIErrorResult {
  if (err instanceof PaymentRequiredError) {
    return { type: 'payment_required' }
  }
  if (err instanceof TooManyRequestsError) {
    return { type: 'rate_limit', seconds: err.retryAfter }
  }
  if (err instanceof Error) {
    return { type: 'generic', message: err.message }
  }
  return { type: 'generic', message: 'Đã có lỗi xảy ra. Vui lòng thử lại.' }
}
