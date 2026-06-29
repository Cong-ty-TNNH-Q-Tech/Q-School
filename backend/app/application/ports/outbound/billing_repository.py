import uuid
from abc import ABC, abstractmethod
from typing import Optional

from app.domain.models.billing import Plan, UserSubscription, PaymentTransaction

class IBillingRepository(ABC):
    """
    Port (Interface) cho các thao tác với Plan, Subscription, Payment.
    """

    @abstractmethod
    async def get_plan_by_id(self, plan_id: uuid.UUID) -> Optional[Plan]:
        pass

    @abstractmethod
    async def get_active_subscription(self, user_id: uuid.UUID) -> Optional[UserSubscription]:
        pass

    @abstractmethod
    async def create_transaction(self, transaction: PaymentTransaction) -> PaymentTransaction:
        pass

    @abstractmethod
    async def get_transaction_by_id(self, transaction_id: uuid.UUID) -> Optional[PaymentTransaction]:
        pass

    @abstractmethod
    async def update_transaction(self, transaction: PaymentTransaction) -> PaymentTransaction:
        pass

    @abstractmethod
    async def create_subscription(self, subscription: UserSubscription) -> UserSubscription:
        pass

    @abstractmethod
    async def update_subscription(self, subscription: UserSubscription) -> UserSubscription:
        pass
