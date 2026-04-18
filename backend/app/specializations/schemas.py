from pydantic import BaseModel
from typing import Optional

class SpecializationCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    icon: Optional[str] = "local_hospital"

class SpecializationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
