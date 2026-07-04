import { CreditCard, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface PaymentRequiredBannerProps {
  onUpgrade?: () => void;
}

export function PaymentRequiredBanner({ onUpgrade }: PaymentRequiredBannerProps) {
  return (
    // [FIX Phase6-B5] role="alert" — Screen Reader thông báo ngay khi component mount
    <div
      role="alert"
      aria-live="assertive"
      className="bg-rose-50 border border-rose-200 rounded-xl p-4 mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-in fade-in slide-in-from-top-2 duration-300"
    >
      <div className="flex items-start sm:items-center gap-3">
        <div className="p-2 bg-rose-100 rounded-full shrink-0" aria-hidden="true">
          <CreditCard className="w-5 h-5 text-rose-600" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-rose-900">Bạn đã hết lượt sử dụng công cụ AI</h4>
          <p className="text-sm text-rose-700 mt-0.5">
            Gói cước hiện tại của bạn đã đạt giới hạn. Vui lòng nâng cấp để tiếp tục sử dụng không giới hạn.
          </p>
        </div>
      </div>
      <Button
        onClick={onUpgrade}
        className="shrink-0 w-full sm:w-auto bg-rose-600 hover:bg-rose-700 text-white"
        size="sm"
        type="button"
      >
        Nâng cấp gói cước
      </Button>
    </div>
  );
}

interface RateLimitWarningProps {
  secondsLeft: number;
}

export function RateLimitWarning({ secondsLeft }: RateLimitWarningProps) {
  if (secondsLeft <= 0) return null;

  return (
    // [FIX Phase6-B5] role="alert" + aria-live="polite" (không assertive — countdown không cần interrupt)
    <div
      role="alert"
      aria-live="polite"
      className="bg-amber-50 border border-amber-200 rounded-xl p-3 mb-6 flex items-center gap-3 animate-in fade-in slide-in-from-top-2 duration-300"
    >
      <AlertCircle className="w-5 h-5 text-amber-600 shrink-0" aria-hidden="true" />
      <p className="text-sm text-amber-800">
        Bạn đang gửi yêu cầu quá nhanh. Vui lòng thử lại sau{' '}
        <span className="font-bold" aria-label={`${secondsLeft} giây`}>{secondsLeft}</span> giây.
      </p>
    </div>
  );
}
