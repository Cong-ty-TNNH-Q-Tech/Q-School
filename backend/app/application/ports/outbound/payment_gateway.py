from abc import ABC, abstractmethod
from typing import Dict, Any

from app.domain.models.billing import PaymentStatus

class IPaymentGateway(ABC):
    """
    Port (Interface) giao tiếp với các cổng thanh toán (Strategy Pattern).
    """

    @abstractmethod
    async def create_checkout_session(
        self, 
        transaction_id: str, 
        amount: int, 
        description: str,
        return_url: str
    ) -> str:
        """
        Khởi tạo luồng thanh toán và trả về Checkout URL.
        """
        pass

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Xác thực chữ ký của Webhook (IPN) gửi từ cổng thanh toán.
        """
        pass

    @abstractmethod
    def parse_webhook_event(self, payload: bytes) -> Dict[str, Any]:
        """
        Phân tích payload của Webhook và trả về dict chuẩn hóa.
        Return dict chứa ít nhất:
        {
            "transaction_id": str (UUID của PaymentTransaction),
            "status": PaymentStatus,
            "provider_transaction_id": str
        }
        """
        pass
