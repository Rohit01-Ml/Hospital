from pydantic import BaseModel
from typing import Optional

class LabTestTypeCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float
    turnaround_hours: int = 6
    category: str = "General"

class LabTestTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    turnaround_hours: Optional[int] = None
    category: Optional[str] = None

class LabBookingCreate(BaseModel):
    test_type_id: str
    appointment_id: Optional[str] = None
    notes: Optional[str] = ""

class LabBookingStatusUpdate(BaseModel):
    status: str  # booked | sample_collected | processing | report_ready | cancelled
    payment_status: Optional[str] = None
