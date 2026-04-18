from pydantic import BaseModel
from typing import Optional

class AppointmentCreate(BaseModel):
    doctor_id: str
    specialization_id: str
    date: str       # YYYY-MM-DD
    time_slot: str  # HH:MM
    notes: Optional[str] = ""
    patient_id: Optional[str] = None        # staff: book for a specific patient
    payment_method: Optional[str] = None    # "cash" | "upi" | "online"

class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
