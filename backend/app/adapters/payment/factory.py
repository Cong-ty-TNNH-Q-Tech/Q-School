from app.application.ports.outbound.payment_gateway import IPaymentGateway
from app.adapters.payment.sepay_adapter import SePayPaymentAdapter
from app.domain.models.billing import PaymentProvider
from app.core.config import settings

class PaymentGatewayFactory:
    @staticmethod
    def get_gateway(provider: PaymentProvider) -> IPaymentGateway:
        if provider == PaymentProvider.SEPAY:
            return SePayPaymentAdapter(
                api_token=settings.SEPAY_API_TOKEN, 
                webhook_token=settings.SEPAY_WEBHOOK_SECRET,
                acc=settings.SEPAY_ACCOUNT_NUMBER,
                bank=settings.SEPAY_BANK
            )
        else:
            raise ValueError(f"Provider {provider} không được hỗ trợ")
