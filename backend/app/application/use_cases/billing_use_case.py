import uuid
import logging
from typing import Dict, Any

from app.application.ports.outbound.billing_repository import IBillingRepository
from app.adapters.payment.factory import PaymentGatewayFactory
from app.domain.models.billing import PaymentTransaction, PaymentStatus, PaymentProvider
from app.domain.exceptions import PlanNotFoundError, PaymentTransactionNotFoundError, InvalidPaymentWebhookError

logger = logging.getLogger(__name__)

class CreateCheckoutSessionUseCase:
    def __init__(self, billing_repo: IBillingRepository):
        self.billing_repo = billing_repo

    async def execute(self, user_id: uuid.UUID, plan_id: uuid.UUID, provider: PaymentProvider) -> Dict[str, Any]:
        logger.info(f"Khởi tạo thanh toán cho user {user_id}, plan {plan_id}, qua {provider}")
        
        # 1. Lấy thông tin Plan
        plan = await self.billing_repo.get_plan_by_id(plan_id)
        if not plan:
            raise PlanNotFoundError("Gói cước không tồn tại")
            
        if not plan.is_active:
            raise PlanNotFoundError("Gói cước hiện không khả dụng")

        # 2. Tạo Transaction (pending)
        transaction = PaymentTransaction(
            user_id=user_id,
            amount=plan.price,
            currency="VND",
            provider=provider,
            status=PaymentStatus.PENDING
        )
        # TODO: Link transaction với subscription_id nếu đang renew hoặc lưu tạm plan_id vào metadata. 
        # Vì đây là ví dụ, ta lưu transaction
        transaction = await self.billing_repo.create_transaction(transaction)
        
        # 3. Lấy Gateway Adapter
        gateway = PaymentGatewayFactory.get_gateway(provider)
        
        # 4. Khởi tạo checkout session
        return_url = f"https://qschool.vn/payment/callback"
        description = f"Thanh toan goi {plan.name} cho user {user_id}"
        
        checkout_url = await gateway.create_checkout_session(
            transaction_id=str(transaction.id),
            amount=plan.price,
            description=description,
            return_url=return_url
        )
        
        return {
            "checkout_url": checkout_url,
            "transaction_id": str(transaction.id)
        }

class ProcessWebhookUseCase:
    def __init__(self, billing_repo: IBillingRepository):
        self.billing_repo = billing_repo

    async def execute(self, provider: PaymentProvider, payload: bytes, signature: str) -> None:
        logger.info(f"Xử lý Webhook từ {provider}")
        
        gateway = PaymentGatewayFactory.get_gateway(provider)
        
        # 1. Verify signature
        if not gateway.verify_webhook_signature(payload, signature):
            raise InvalidPaymentWebhookError("Chữ ký Webhook không hợp lệ")
            
        # 2. Parse event
        event_data = gateway.parse_webhook_event(payload)
        transaction_id_str = event_data.get("transaction_id")
        status = event_data.get("status")
        provider_transaction_id = event_data.get("provider_transaction_id")
        transfer_amount = event_data.get("transfer_amount", 0)
        
        if not transaction_id_str:
            raise InvalidPaymentWebhookError("Không tìm thấy transaction_id trong payload")
            
        try:
            transaction_uuid = uuid.UUID(transaction_id_str)
        except ValueError:
            raise InvalidPaymentWebhookError(f"transaction_id không hợp lệ: {transaction_id_str}")
            
        # 3. Get transaction
        transaction = await self.billing_repo.get_transaction_by_id(transaction_uuid)
        if not transaction:
            raise PaymentTransactionNotFoundError("Transaction không tồn tại")
            
        # 4. Idempotency check: Tránh duplicate xử lý
        if transaction.status != PaymentStatus.PENDING:
            logger.warning(f"Transaction {transaction.id} đã được xử lý (Status: {transaction.status})")
            return
            
        # 5. Cập nhật transaction status
        if status == PaymentStatus.SUCCESS and transfer_amount < transaction.amount:
            logger.warning(f"Số tiền chuyển ({transfer_amount}) nhỏ hơn yêu cầu ({transaction.amount}) cho transaction {transaction.id}")
            status = PaymentStatus.FAILED

        transaction.status = status
        transaction.provider_transaction_id = provider_transaction_id
        await self.billing_repo.update_transaction(transaction)
        
        # 6. Nếu success, update subscription
        if status == PaymentStatus.SUCCESS:
            logger.info(f"Thanh toán thành công cho transaction {transaction.id}. Cập nhật subscription...")
            # TODO: Cập nhật hoặc tạo mới UserSubscription cho user (Cần lưu plan_id lúc tạo transaction)
            # Vì entity PaymentTransaction có liên kết subscription_id, ta có thể cập nhật ở đây.
