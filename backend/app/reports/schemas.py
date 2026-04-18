from pydantic import BaseModel
from typing import Optional

class ReportCreate(BaseModel):
    patient_id: str
    lab_booking_id: Optional[str] = None
    test_type_id: Optional[str] = None
    title: str
    findings: str
    interpretation: Optional[str] = ""
    status: str = "normal"   # normal | abnormal | critical
    file_url: Optional[str] = None

class ReportUpdate(BaseModel):
    title: Optional[str] = None
    findings: Optional[str] = None
    interpretation: Optional[str] = None
    status: Optional[str] = None
    file_url: Optional[str] = None
