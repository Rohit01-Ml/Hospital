from pydantic import BaseModel
from typing import Optional

class DoctorCreate(BaseModel):
    name: str
    specialization_id: str
    experience_years: int
    qualification: str
    phone: Optional[str] = ""
    email: Optional[str] = ""
    bio: Optional[str] = ""
    available: bool = True

class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    specialization_id: Optional[str] = None
    experience_years: Optional[int] = None
    qualification: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    available: Optional[bool] = None

class AvailabilityCreate(BaseModel):
    doctor_id: str
    day_of_week: int       # 0=Monday … 6=Sunday
    start_time: str        # "HH:MM"
    end_time: str          # "HH:MM"
    slot_duration_minutes: int = 20
    max_patients: int = 12

class AvailabilityUpdate(BaseModel):
    day_of_week: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    slot_duration_minutes: Optional[int] = None
    max_patients: Optional[int] = None
