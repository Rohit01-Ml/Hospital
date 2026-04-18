from pydantic import BaseModel

class QueueAction(BaseModel):
    action: str  # next | skip | complete
    appointment_id: str
