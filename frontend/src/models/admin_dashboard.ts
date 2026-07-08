/**
 * Interfaces cho Admin Dashboard Stats & Activity
 * Định nghĩa theo thực thể trong erd_schema.md và mock data.
 */

export interface AdminUserStats {
  total_users: number;
  total_teachers: number;
  total_students: number;
  total_admins: number;
  new_users_this_month: number;
  active_users_today: number;
}

export interface AdminRevenueStats {
  total_revenue: number;        // VNĐ
  monthly_revenue: number;      // VNĐ
  active_subscriptions: number;
  revenue_growth_percent: number; // % so với tháng trước
}

export interface SystemHealthStats {
  status: 'healthy' | 'warning' | 'critical';
  uptime_percent: number;
  ai_service_status: 'online' | 'degraded' | 'offline';
  storage_used_percent: number;
  active_ai_tasks: number;
}

export interface RecentUserActivity {
  id: string;
  user_id: string;
  username: string;
  full_name: string | null;
  action: 'registered' | 'login' | 'subscription_changed' | 'content_created';
  role: 'student' | 'teacher' | 'admin';
  detail: string;
  created_at: string; // ISO Datetime
}

export interface AdminDashboardData {
  user_stats: AdminUserStats;
  revenue_stats: AdminRevenueStats;
  system_health: SystemHealthStats;
  recent_activities: RecentUserActivity[];
}
