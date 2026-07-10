import { create } from 'zustand';
import type { AdminDashboardData } from '@/models/admin_dashboard';
import { mockAdminDashboardResponse } from '@/services/mockData/admin_dashboard.mock';

interface AdminDashboardState {
  data: AdminDashboardData | null;
  isLoading: boolean;
  error: string | null;
  fetchDashboardData: () => Promise<void>;
}

export const useAdminDashboard = create<AdminDashboardState>((set) => ({
  data: null,
  isLoading: false,
  error: null,
  fetchDashboardData: async () => {
    set({ isLoading: true, error: null });
    try {
      // Giả lập độ trễ mạng (API Delay 500ms theo rule/pattern dự án)
      await new Promise((resolve) => setTimeout(resolve, 500));
      
      if (mockAdminDashboardResponse.status === 'success') {
        set({ data: mockAdminDashboardResponse.data, isLoading: false });
      } else {
        throw new Error(mockAdminDashboardResponse.message || 'Lỗi khi tải thông tin Dashboard');
      }
    } catch (error: unknown) {
      const err = error as Error;
      set({ error: err.message || 'Đã xảy ra lỗi không xác định', isLoading: false });
    }
  },
}));
