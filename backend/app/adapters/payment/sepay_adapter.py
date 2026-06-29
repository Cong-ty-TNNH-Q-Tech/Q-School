import json
from typing import Dict, Any
from app.application.ports.outbound.payment_gateway import IPaymentGateway
from app.domain.models.billing import PaymentStatus

class SePayPaymentAdapter(IPaymentGateway):
    def __init__(self, api_token: str, webhook_token: str):
        self.api_token = api_token
        self.webhook_token = webhook_token

    async def create_checkout_session(
        self, 
        transaction_id: str, 
        amount: int, 
        description: str,
        return_url: str
    ) -> str:
        # SePay thường không tạo session như Stripe. 
        # Nó cung cấp link thanh toán hoặc mã QR để quét (Ví dụ chuyển khoản).
        # Thay vì redirect tới gateway, ta trả về thông tin hoặc trang hướng dẫn chuyển khoản.
        # Ở đây ta trả về URL giả lập hiển thị QR Code chuyển khoản với nội dung là transaction_id
        return f"https://my.sepay.vn/pay?amount={amount}&content={transaction_id}"

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        # SePay xác thực webhook qua API Key (Authorization header chứa webhook_token)
        # Signature ở đây chính là Authorization header nhận được từ Webhook request
        return signature == f"Bearer {self.webhook_token}"

    def parse_webhook_event(self, payload: bytes) -> Dict[str, Any]:
        """
        Payload của SePay gửi dạng JSON chứa các trường như:
        id, gateway, transactionDate, accountName, accountNumber, subAccount,
        transferType, transferAmount, accumulated, code, transactionContent,
        referenceNumber, body
        """
        event = json.loads(payload)
        
        # transaction_id lấy từ transactionContent (nội dung chuyển khoản)
        transaction_id = event.get("transactionContent", "").strip()
        
        # Nếu transferAmount > 0 và transferType == "in" thì là nạp tiền thành công
        # Vì đơn giản, chỉ ghi nhận thành công
        
        return {
            "transaction_id": transaction_id, 
            "status": PaymentStatus.SUCCESS,
            "provider_transaction_id": str(event.get("id"))
        }
