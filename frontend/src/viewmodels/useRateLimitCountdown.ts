import { useEffect, type Dispatch, type SetStateAction } from 'react'

/**
 * Shared custom hook to handle the rate limit countdown timer.
 */
export function useRateLimitCountdown(
  rateLimitSeconds: number,
  setRateLimitSeconds: Dispatch<SetStateAction<number>>
) {
  useEffect(() => {
    if (rateLimitSeconds > 0) {
      const timer = setTimeout(() => setRateLimitSeconds(prev => prev - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [rateLimitSeconds, setRateLimitSeconds])
}
