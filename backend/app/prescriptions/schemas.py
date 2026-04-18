from pydantic import BaseModel
from typing import Optional, List

class MedicineItem(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str
    instructions: Optional[str] = ""

class PrescriptionCreate(BaseModel):
    appointment_id: str
    patient_id: str
    diagnosis: str
    medicines: List[MedicineItem]
    notes: Optional[str] = ""
    follow_up_date: Optional[str] = None

class PrescriptionUpdate(BaseModel):
    diagnosis: Optional[str] = None
    medicines: Optional[List[MedicineItem]] = None
    notes: Optional[str] = None
    follow_up_date: Optional[str] = None
