export interface StudentStats {
  upcomingAssignments: number;
  averageScore: number;
  flashcardsToReview: number;
}

export interface Activity {
  id: string;
  title: string;
  type: 'assignment' | 'flashcard' | 'lesson';
  date: string;
  status: 'completed' | 'pending' | 'upcoming';
}

export interface StudentDashboardData {
  stats: StudentStats;
  recentActivities: Activity[];
}
