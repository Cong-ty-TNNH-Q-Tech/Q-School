/**
 * SaaS Billing TypeScript Models
 */

export type PlanName = 'Free' | 'Pro' | 'Enterprise'
export type BillingCycle = 'monthly' | 'yearly'
export type SubscriptionStatus = 'active' | 'past_due' | 'canceled'
export type PaymentProvider = 'stripe' | 'vnpay' | 'momo'
export type PaymentStatus = 'pending' | 'success' | 'failed'

export interface PlanFeatures {
  max_ai_chat_per_day: number    // -1 = unlimited
  max_documents: number          // -1 = unlimited
  max_classes: number            // -1 = unlimited
  [key: string]: number
}

export interface Plan {
  id: string
  name: PlanName
  billing_cycle: BillingCycle
  price: number                  // VNĐ
  features: PlanFeatures
  is_active: boolean
}

export interface UserSubscription {
  id: string
  user_id: string
  plan_id: string
  plan?: Plan
  status: SubscriptionStatus
  current_period_start: string
  current_period_end: string
  canceled_at: string | null
}

export interface PaymentTransaction {
  id: string
  user_id: string
  subscription_id: string | null
  amount: number
  currency: string
  provider: PaymentProvider
  provider_transaction_id: string | null
  status: PaymentStatus
  created_at: string
}
