from pydantic import BaseModel
from typing import Optional, List

class MedicineReminderCreate(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str   # once_daily | twice_daily | thrice_daily | once_weekly | as_needed
    times: List[str] # ["08:00", "20:00"]
    start_date: str
    end_date: Optional[str] = None
    instructions: Optional[str] = ""
    prescription_id: Optional[str] = None

class MedicineReminderUpdate(BaseModel):
    medicine_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    times: Optional[List[str]] = None
    end_date: Optional[str] = None
    instructions: Optional[str] = None
    active: Optional[bool] = None
