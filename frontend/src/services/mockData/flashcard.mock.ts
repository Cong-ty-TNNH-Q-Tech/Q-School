import type { FlashcardSet, Flashcard } from '@/models/quiz';

export const mockFlashcardSets: FlashcardSet[] = [
  {
    id: 'set-1',
    creator_id: 'teacher-1',
    title: 'Biology 101 - Ecosystems',
    card_count: 20,
    created_at: '2026-05-01T10:00:00Z',
  },
  {
    id: 'set-2',
    creator_id: 'teacher-1',
    title: 'English Vocabulary - Unit 5',
    card_count: 15,
    created_at: '2026-05-02T10:00:00Z',
  },
  {
    id: 'set-3',
    creator_id: 'teacher-2',
    title: 'Lịch sử Việt Nam - Triều Nguyễn',
    card_count: 30,
    created_at: '2026-05-03T10:00:00Z',
  }
];

// Generate 20 mock cards for set-1
export const mockFlashcards: Flashcard[] = Array.from({ length: 20 }).map((_, index) => ({
  id: `card-${index + 1}`,
  set_id: 'set-1',
  front_text: index === 4 ? 'Photosynthesis' : `Concept ${index + 1} (Mặt trước)`,
  back_text: index === 4 ? 'Quá trình quang hợp, chuyển đổi năng lượng ánh sáng thành năng lượng hóa học.' : `Định nghĩa chi tiết cho Concept ${index + 1} (Mặt sau)`,
  media_url: null
}));

// Mock API Functions mimicking the backend standard response
export const FlashcardMockService = {
  getFlashcardSets: async (): Promise<{ status: string; data: FlashcardSet[] }> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          status: 'success',
          data: mockFlashcardSets
        });
      }, 500);
    });
  },

  getFlashcardSet: async (setId: string): Promise<{ status: string; data: FlashcardSet | null }> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const set = mockFlashcardSets.find(s => s.id === setId) || null;
        resolve({
          status: 'success',
          data: set
        });
      }, 500);
    });
  },

  getCardsForReview: async (setId: string): Promise<{ status: string; data: Flashcard[] }> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const cards = setId === 'set-1' ? mockFlashcards : mockFlashcards.slice(0, 5); // Just some dummy data
        resolve({
          status: 'success',
          data: cards
        });
      }, 500);
    });
  },

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  submitReview: async (_flashcardId: string, _confidenceLevel: 1 | 2 | 3 | 4 | 5): Promise<{ status: string; data: Record<string, unknown> }> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          status: 'success',
          data: {
            review_id: `review-${Date.now()}`,
            next_review_at: new Date(Date.now() + 86400000).toISOString() // Next day
          }
        });
      }, 300);
    });
  }
};
