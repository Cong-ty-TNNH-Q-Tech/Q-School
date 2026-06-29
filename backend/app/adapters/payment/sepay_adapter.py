import json
from typing import Dict, Any
from app.application.ports.outbound.payment_gateway import IPaymentGateway
from app.domain.models.billing import PaymentStatus

class SePayPaymentAdapter(IPaymentGateway):
    def __init__(self, api_token: str, webhook_token: str, acc: str, bank: str):
        self.api_token = api_token
        self.webhook_token = webhook_token
        self.acc = acc
        self.bank = bank

    async def create_checkout_session(
        self, 
        transaction_id: str, 
        amount: int, 
        description: str,
        return_url: str
    ) -> str:
        # SePay sử dụng API tạo VietQR động
        # Định dạng: https://qr.sepay.vn/img?acc={acc}&bank={bank}&amount={amount}&des={transaction_id}
        return f"https://qr.sepay.vn/img?acc={self.acc}&bank={self.bank}&amount={amount}&des={transaction_id}"

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        # SePay gửi API Key trong Header Authorization, dạng 'Apikey {token}' hoặc 'Bearer {token}'
        if not signature:
            return False
        token = signature.split(" ")[-1]
        return token == self.webhook_token

    def parse_webhook_event(self, payload: bytes) -> Dict[str, Any]:
        """
        Payload JSON của SePay Webhook chứa: id, gateway, transactionDate, accountNumber,
        content, transferType, transferAmount, accumulated, referenceCode...
        """
        event = json.loads(payload)
        
        # Nội dung chuyển khoản chứa transaction_id
        transaction_id = event.get("content", "").strip()
        transfer_type = event.get("transferType", "in")
        
        # Nếu không phải là tiền vào, ta đánh fail (tránh update nhầm)
        status = PaymentStatus.SUCCESS if transfer_type == "in" else PaymentStatus.FAILED
        
        return {
            "transaction_id": transaction_id, 
            "status": status,
            "provider_transaction_id": str(event.get("id"))
        }
