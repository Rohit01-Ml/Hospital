"""Hospital tenant management — SaaS multi-tenant support."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.mock_data import hospitals_db, next_id
from app.dependencies import require_admin
from datetime import datetime

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])

PLANS = {
    "starter":      {"price": 1999,  "doctors": 5,   "features": ["appointments", "queue"]},
    "professional": {"price": 4999,  "doctors": 20,  "features": ["appointments", "queue", "lab_tests", "reports", "ai_features"]},
    "enterprise":   {"price": 9999,  "doctors": -1,  "features": ["appointments", "queue", "lab_tests", "reports", "ai_features", "websocket", "whatsapp", "api_access"]},
}

class HospitalCreate(BaseModel):
    name: str
    slug: str
    admin_email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    subscription: str = "starter"

class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    subscription: Optional[str] = None
    active: Optional[bool] = None


@router.get("/")
def list_hospitals(current_user: dict = Depends(require_admin)):
    return hospitals_db

@router.get("/plans")
def get_plans():
    """Public — pricing plans for the SaaS landing page."""
    return PLANS

@router.get("/{hospital_id}")
def get_hospital(hospital_id: str, current_user: dict = Depends(require_admin)):
    h = next((h for h in hospitals_db if h["id"] == hospital_id), None)
    if not h:
        raise HTTPException(404, "Hospital not found")
    return h

@router.post("/")
def create_hospital(req: HospitalCreate, current_user: dict = Depends(require_admin)):
    if any(h["slug"] == req.slug for h in hospitals_db):
        raise HTTPException(400, "Slug already taken")
    hospital = {
        "id": next_id("hospital"),
        "name": req.name,
        "slug": req.slug,
        "subscription": req.subscription,
        "admin_email": req.admin_email,
        "phone": req.phone,
        "address": req.address,
        "logo_url": None,
        "active": True,
        "created_at": datetime.utcnow().date().isoformat(),
        "plan_features": PLANS.get(req.subscription, PLANS["starter"])["features"],
        "monthly_fee": PLANS.get(req.subscription, PLANS["starter"])["price"],
    }
    hospitals_db.append(hospital)
    return hospital

@router.put("/{hospital_id}")
def update_hospital(hospital_id: str, req: HospitalUpdate, current_user: dict = Depends(require_admin)):
    h = next((h for h in hospitals_db if h["id"] == hospital_id), None)
    if not h:
        raise HTTPException(404, "Hospital not found")
    for field, val in req.model_dump(exclude_none=True).items():
        h[field] = val
    if req.subscription:
        h["plan_features"] = PLANS.get(req.subscription, PLANS["starter"])["features"]
        h["monthly_fee"] = PLANS.get(req.subscription, PLANS["starter"])["price"]
    return h

@router.delete("/{hospital_id}")
def delete_hospital(hospital_id: str, current_user: dict = Depends(require_admin)):
    global hospitals_db
    h = next((h for h in hospitals_db if h["id"] == hospital_id), None)
    if not h:
        raise HTTPException(404, "Hospital not found")
    hospitals_db[:] = [x for x in hospitals_db if x["id"] != hospital_id]
    return {"message": "Hospital deleted"}
