from app.application.ports.outbound.payment_gateway import IPaymentGateway
from app.adapters.payment.sepay_adapter import SePayPaymentAdapter
from app.domain.models.billing import PaymentProvider

class PaymentGatewayFactory:
    @staticmethod
    def get_gateway(provider: PaymentProvider) -> IPaymentGateway:
        if provider == PaymentProvider.SEPAY:
            # TODO: Lấy config từ settings
            return SePayPaymentAdapter(api_token="sepay_api_token", webhook_token="sepay_webhook_secret")
        else:
            raise ValueError(f"Provider {provider} không được hỗ trợ")
