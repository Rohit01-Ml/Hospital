from pydantic import BaseModel
from typing import Optional

class NotificationCreate(BaseModel):
    user_id: str
    type: str          # appointment_reminder | report_ready | payment_success | follow_up_reminder | prescription_ready | medicine_reminder
    title: str
    message: str
    action_url: Optional[str] = None

class NotificationChannel(BaseModel):
    """Extensible for WhatsApp, SMS, Email, Push"""
    channel: str = "in_app"   # in_app | email | sms | whatsapp
    user_id: str
    message: str
    phone: Optional[str] = None
    email: Optional[str] = None
