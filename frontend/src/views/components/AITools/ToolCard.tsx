import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { ArrowRight } from 'lucide-react';
import type { ReactNode } from 'react';

interface ToolCardProps {
  title: string;
  description: string;
  // [FIX #6] Tách thành 2 prop riêng biệt để tránh logic colorClass apply vào sai element
  icon: ReactNode;
  to: string;
  gradientClass?: string;
  iconColorClass?: string;
  badge?: string;
}

export function ToolCard({
  title,
  description,
  icon,
  to,
  gradientClass = "from-blue-500/10 to-blue-600/10",
  iconColorClass = "text-blue-600",
  badge
}: ToolCardProps) {
  return (
    <Link
      to={to}
      className="group relative flex flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition-all hover:shadow-md hover:border-primary/30 hover:-translate-y-1"
    >
      {/* Background glow decoration — chỉ dùng gradient class */}
      <div className={cn(
        "absolute -right-12 -top-12 h-32 w-32 rounded-full bg-gradient-to-br opacity-50 transition-transform group-hover:scale-150 blur-2xl",
        gradientClass
      )}></div>

      <div className="relative flex items-center justify-between mb-4">
        {/* Icon wrapper — dùng cả gradient + icon color riêng */}
        <div className={cn(
          "flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br shadow-inner",
          gradientClass,
          iconColorClass
        )}>
          {icon}
        </div>
        {badge && (
          <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
            {badge}
          </span>
        )}
      </div>

      <h3 className="relative text-lg font-semibold text-gray-900 mb-2">
        {title}
      </h3>

      <p className="relative text-sm text-gray-500 mb-6 flex-1">
        {description}
      </p>

      <div className="relative flex items-center text-sm font-medium text-primary mt-auto">
        Trải nghiệm ngay
        <ArrowRight className="ml-1.5 h-4 w-4 transition-transform group-hover:translate-x-1" />
      </div>
    </Link>
  );
}
