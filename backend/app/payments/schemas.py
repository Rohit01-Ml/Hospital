from pydantic import BaseModel
from typing import Optional

class PaymentInitiate(BaseModel):
    appointment_id: str
    amount: float
    currency: str = "INR"

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: Optional[str] = None
    appointment_id: Optional[str] = None
