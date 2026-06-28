import type { StudentDashboardData } from '../../models/student_dashboard';

export const mockStudentDashboardResponse = {
  status: 'success',
  data: {
    stats: {
    upcomingAssignments: 3,
    averageScore: 85,
    flashcardsToReview: 24,
  },
  recentActivities: [
    {
      id: '1',
      title: 'Math Homework - Algebra',
      type: 'assignment',
      date: '2026-06-25T10:00:00Z',
      status: 'completed',
    },
    {
      id: '2',
      title: 'Biology Chapter 4 Flashcards',
      type: 'flashcard',
      date: '2026-06-28T08:00:00Z',
      status: 'pending',
    },
    {
      id: '3',
      title: 'Physics Midterm Prep',
      type: 'lesson',
      date: '2026-06-29T14:00:00Z',
      status: 'upcoming',
    },
    {
      id: '4',
      title: 'History Essay',
      type: 'assignment',
      date: '2026-06-30T23:59:00Z',
      status: 'upcoming',
    },
  ],
  } as StudentDashboardData,
  message: 'Fetched student dashboard successfully',
};
