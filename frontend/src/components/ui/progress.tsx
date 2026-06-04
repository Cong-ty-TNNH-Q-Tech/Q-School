import * as React from "react"
import { cn } from "@/lib/utils"

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number
  max?: number
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value = 0, max = 100, ...props }, ref) => {
    // Ensure value is between 0 and max
    const safeValue = Math.min(Math.max(value, 0), max)
    const percentage = max > 0 ? (safeValue / max) * 100 : 0

    return (
      <div
        ref={ref}
        className={cn(
          "relative h-2 w-full overflow-hidden rounded-full bg-secondary/20 bg-gray-200",
          className
        )}
        {...props}
      >
        <div
          className="h-full w-full flex-1 bg-[#5441E7] transition-all duration-500 ease-in-out"
          style={{ transform: `translateX(-${100 - percentage}%)` }}
        />
      </div>
    )
  }
)
Progress.displayName = "Progress"

export { Progress }
