"""
SaaS Billing ORM Models — Plan, UserSubscription, PaymentTransaction
Group 4: Billing & Subscriptions
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    String,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.models.base import UUIDMixin, TimestampMixin
import enum

class PaymentProvider(str, enum.Enum):
    SEPAY = "sepay"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

if TYPE_CHECKING:
    from app.domain.models.user import User


class Plan(Base, UUIDMixin):
    """
    Bảng PLANS — Cấu hình gói cước (Free, Pro, Enterprise).
    features: JSONB chứa các giới hạn (VD: {"max_ai_chat_per_day": 5, "max_documents": 10})
    """

    __tablename__ = "plans"
    __table_args__ = (
        CheckConstraint(
            "billing_cycle IN ('monthly', 'yearly')", name="ck_plans_billing_cycle"
        ),
    )

    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="Free | Pro | Enterprise"
    )
    billing_cycle: Mapped[str] = mapped_column(
        String(20), nullable=False, default="monthly", comment="monthly | yearly"
    )
    price: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="Giá tính bằng VNĐ (0 = miễn phí)"
    )
    features: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Giới hạn tính năng theo gói: max_ai_chat_per_day, max_documents, etc.",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    subscriptions: Mapped[list["UserSubscription"]] = relationship(
        "UserSubscription", back_populates="plan"
    )

    def __repr__(self) -> str:
        return f"<Plan name={self.name} price={self.price}>"


class UserSubscription(Base, UUIDMixin, TimestampMixin):
    """
    Bảng USER_SUBSCRIPTIONS — Trạng thái gói cước hiện tại của User.
    status: 'active' | 'past_due' | 'canceled'
    """

    __tablename__ = "user_subscriptions"
    __table_args__ = (
        # Composite index cho query "active subscription của user X" — rất phổ biến
        Index("ix_user_subscriptions_user_status", "user_id", "status"),
        CheckConstraint(
            "status IN ('active', 'past_due', 'canceled')",
            name="ck_user_subscriptions_status",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="active | past_due | canceled",
    )
    current_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    current_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
    plan: Mapped["Plan"] = relationship("Plan", back_populates="subscriptions")
    transactions: Mapped[list["PaymentTransaction"]] = relationship(
        "PaymentTransaction", back_populates="subscription"
    )


class PaymentTransaction(Base, UUIDMixin, TimestampMixin):
    """
    Bảng PAYMENT_TRANSACTIONS — Lịch sử giao dịch qua Webhook (Stripe/VNPay).
    status: 'pending' | 'success' | 'failed'
    """

    __tablename__ = "payment_transactions"
    __table_args__ = (
        CheckConstraint(
            "provider IN ('sepay')",
            name="ck_payment_transactions_provider",
        ),
        CheckConstraint(
            "status IN ('pending', 'success', 'failed')",
            name="ck_payment_transactions_status",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user_subscriptions.id"), nullable=True
    )
    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plans.id"), nullable=True, comment="Gói cước đang mua"
    )
    amount: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Số tiền (VNĐ)"
    )
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="VND")
    provider: Mapped[PaymentProvider] = mapped_column(
        String(20), nullable=False, comment="sepay"
    )
    provider_transaction_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="ID giao dịch từ cổng thanh toán"
    )
    status: Mapped[PaymentStatus] = mapped_column(
        String(20),
        nullable=False,
        default=PaymentStatus.PENDING,
        comment="pending | success | failed",
    )

    subscription: Mapped["UserSubscription | None"] = relationship(
        "UserSubscription", back_populates="transactions"
    )
    plan: Mapped["Plan | None"] = relationship("Plan")
