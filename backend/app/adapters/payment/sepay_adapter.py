import json
import re
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
        import secrets
        return secrets.compare_digest(token, self.webhook_token)

    def parse_webhook_event(self, payload: bytes) -> Dict[str, Any]:
        """
        Payload JSON của SePay Webhook chứa: id, gateway, transactionDate, accountNumber,
        content, transferType, transferAmount, accumulated, referenceCode...
        """
        event = json.loads(payload)
        
        content = event.get("content", "").strip()
        transfer_type = event.get("transferType", "in")
        transfer_amount = int(event.get("transferAmount", 0))
        
        # Tìm UUID trong content (hỗ trợ cả có gạch nối và không có gạch nối do một số ngân hàng tự loại bỏ)
        match = re.search(r"[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}", content)
        transaction_id = match.group(0) if match else content
        
        # Nếu không phải là tiền vào, ta đánh fail
        status = PaymentStatus.SUCCESS if transfer_type == "in" else PaymentStatus.FAILED
        
        return {
            "transaction_id": transaction_id, 
            "status": status,
            "provider_transaction_id": str(event.get("id")),
            "transfer_amount": transfer_amount
        }
