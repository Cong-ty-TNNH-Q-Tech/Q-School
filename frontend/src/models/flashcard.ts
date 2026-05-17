/**
 * Flashcard TypeScript Models — Tách riêng từ quiz.ts cho rõ ràng.
 * Re-export từ quiz.ts để tránh breaking changes.
 */
export type { FlashcardSet, Flashcard, FlashcardReview } from './quiz'
