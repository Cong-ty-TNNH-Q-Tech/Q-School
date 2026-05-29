import { useState, useEffect, useCallback } from 'react';
import type { Flashcard } from '@/models/quiz';
import { FlashcardMockService } from '@/services/mockData/flashcard.mock';

export function useFlashcards(setId: string) {
  const [setTitle, setSetTitle] = useState('');
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    const fetchCards = async () => {
      setIsLoading(true);
      try {
        // Fetch set details
        const setResponse = await FlashcardMockService.getFlashcardSet(setId);
        if (setResponse.status === 'success' && setResponse.data) {
          setSetTitle(setResponse.data.title);
        }

        const response = await FlashcardMockService.getCardsForReview(setId);
        if (response.status === 'success') {
          setCards(response.data);
          setCurrentIndex(0);
          setIsFlipped(false);
          setIsCompleted(response.data.length === 0);
        }
      } catch (error) {
        console.error('Failed to fetch flashcards:', error);
      } finally {
        setIsLoading(false);
      }
    };

    if (setId) {
      fetchCards();
    }
  }, [setId]);

  const flipCard = useCallback(() => {
    setIsFlipped(true);
  }, []);

  const submitConfidence = useCallback(async (level: 1 | 2 | 3 | 4 | 5) => {
    if (cards.length === 0 || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const currentCard = cards[currentIndex];
      // Submit the review result to the backend
      await FlashcardMockService.submitReview(currentCard.id, level);

      // Move to the next card
      if (currentIndex < cards.length - 1) {
        setIsFlipped(false);
        // Wait a short time for the flip animation to reset before changing the text
        setTimeout(() => {
          setCurrentIndex((prev) => prev + 1);
        }, 150);
      } else {
        setIsCompleted(true);
      }
    } catch (error) {
      console.error('Failed to submit review:', error);
    } finally {
      setIsSubmitting(false);
    }
  }, [cards, currentIndex, isSubmitting]);

  return {
    setTitle,
    cards,
    currentCard: cards[currentIndex],
    currentIndex,
    totalCards: cards.length,
    isFlipped,
    isLoading,
    isSubmitting,
    isCompleted,
    flipCard,
    submitConfidence
  };
}
