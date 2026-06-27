import { useState, useEffect } from 'react';
import type { FlashcardSet } from '@/models/quiz';
import { FlashcardMockService } from '@/services/mockData/flashcard.mock';

export function useFlashcardSets() {
  const [sets, setSets] = useState<FlashcardSet[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSets = async () => {
      try {
        const response = await FlashcardMockService.getFlashcardSets();
        if (response.status === 'success') {
          setSets(response.data);
        }
      } catch (error) {
        console.error('Failed to fetch flashcard sets:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchSets();
  }, []);

  return { sets, isLoading };
}
