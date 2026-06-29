import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.outbound.billing_repository import IBillingRepository
from app.domain.models.billing import Plan, UserSubscription, PaymentTransaction

class BillingRepository(IBillingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_plan_by_id(self, plan_id: uuid.UUID) -> Optional[Plan]:
        result = await self.session.execute(select(Plan).where(Plan.id == plan_id))
        return result.scalars().first()

    async def get_active_subscription(self, user_id: uuid.UUID) -> Optional[UserSubscription]:
        result = await self.session.execute(
            select(UserSubscription)
            .where(UserSubscription.user_id == user_id)
            .where(UserSubscription.status == "active")
        )
        return result.scalars().first()

    async def create_transaction(self, transaction: PaymentTransaction) -> PaymentTransaction:
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def get_transaction_by_id(self, transaction_id: uuid.UUID) -> Optional[PaymentTransaction]:
        result = await self.session.execute(
            select(PaymentTransaction).where(PaymentTransaction.id == transaction_id)
        )
        return result.scalars().first()

    async def update_transaction(self, transaction: PaymentTransaction) -> PaymentTransaction:
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def create_subscription(self, subscription: UserSubscription) -> UserSubscription:
        self.session.add(subscription)
        await self.session.flush()
        return subscription

    async def update_subscription(self, subscription: UserSubscription) -> UserSubscription:
        self.session.add(subscription)
        await self.session.flush()
        return subscription
