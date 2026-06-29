import uuid
from typing import Dict, Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.entrypoints.api_v1.auth import get_current_user_id
from app.application.use_cases.billing_use_case import CreateCheckoutSessionUseCase, ProcessWebhookUseCase
from app.adapters.database.billing_repository import BillingRepository
from app.domain.models.billing import PaymentProvider

router = APIRouter(prefix="/billing", tags=["Billing"])
webhook_router = APIRouter(prefix="/webhooks/payments", tags=["Billing"])

class CheckoutRequest(BaseModel):
    plan_id: uuid.UUID
    provider: PaymentProvider = Field(default=PaymentProvider.SEPAY)

class CheckoutResponseData(BaseModel):
    checkout_url: str
    transaction_id: str

class CheckoutResponse(BaseModel):
    status: str = "success"
    data: CheckoutResponseData

@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    request: CheckoutRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    repo = BillingRepository(db)
    use_case = CreateCheckoutSessionUseCase(repo)
    result = await use_case.execute(user_id=user_id, plan_id=request.plan_id, provider=request.provider)
    
    # Do we commit here? The usecase should probably have db context or we commit here.
    # It's better to commit in the entrypoint or have unit of work. 
    # For now we'll commit here.
    await db.commit()
    
    return CheckoutResponse(
        status="success",
        data=CheckoutResponseData(
            checkout_url=result["checkout_url"],
            transaction_id=result["transaction_id"]
        )
    )

@webhook_router.post("")
async def receive_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Lấy payload thô
    payload = await request.body()
    
    # SePay truyền token qua header Authorization
    signature = request.headers.get("Authorization", "")
    
    repo = BillingRepository(db)
    use_case = ProcessWebhookUseCase(repo)
    
    await use_case.execute(
        provider=PaymentProvider.SEPAY,
        payload=payload,
        signature=signature
    )
    
    await db.commit()
    
    return {"success": True}
