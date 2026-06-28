import { create } from 'zustand';
import type { StudentDashboardData } from '@/models/student_dashboard';
import { mockStudentDashboardResponse } from '@/services/mockData/student_dashboard.mock';

interface StudentDashboardState {
  data: StudentDashboardData | null;
  isLoading: boolean;
  error: string | null;
  fetchDashboardData: () => Promise<void>;
}

export const useStudentDashboard = create<StudentDashboardState>((set) => ({
  data: null,
  isLoading: false,
  error: null,
  fetchDashboardData: async () => {
    set({ isLoading: true, error: null });
    try {
      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 500));
      
      if (mockStudentDashboardResponse.status === 'success') {
        set({ data: mockStudentDashboardResponse.data, isLoading: false });
      } else {
        throw new Error(mockStudentDashboardResponse.message || 'Failed to fetch dashboard data');
      }
    } catch (error: unknown) {
      const err = error as Error;
      set({ error: err.message || 'An error occurred', isLoading: false });
    }
  },
}));
