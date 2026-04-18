from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.lab_tests.schemas import LabTestTypeCreate, LabTestTypeUpdate, LabBookingCreate, LabBookingStatusUpdate
from app.mock_data import lab_test_types_db, lab_bookings_db, users_db, notifications_db, next_id
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/lab-tests", tags=["Lab Tests"])

def _enrich_booking(b: dict) -> dict:
    test_type = next((t for t in lab_test_types_db if t["id"] == b["test_type_id"]), None)
    patient   = next((u for u in users_db if u["id"] == b["patient_id"]), None)
    return {**b, "test_type": test_type, "patient_name": patient["name"] if patient else "Unknown"}

def _notify_report(patient_id: str, test_name: str):
    notifications_db.append({
        "id": next_id("notification"),
        "user_id": patient_id,
        "type": "report_ready",
        "title": "Lab Report Ready",
        "message": f"Your {test_name} report is ready. Click to view.",
        "read": False,
        "action_url": "/patient/reports",
        "created_at": datetime.utcnow().isoformat(),
    })

# ── Test Types ─────────────────────────────────────────────────────────────────
@router.get("/types")
def list_test_types():
    return lab_test_types_db

@router.get("/types/{type_id}")
def get_test_type(type_id: str):
    t = next((x for x in lab_test_types_db if x["id"] == type_id), None)
    if not t:
        raise HTTPException(404, "Test type not found")
    return t

@router.post("/types", dependencies=[Depends(require_admin)])
def create_test_type(req: LabTestTypeCreate):
    t = {"id": next_id("lab_test_type"), **req.model_dump()}
    lab_test_types_db.append(t)
    return t

@router.put("/types/{type_id}", dependencies=[Depends(require_admin)])
def update_test_type(type_id: str, req: LabTestTypeUpdate):
    t = next((x for x in lab_test_types_db if x["id"] == type_id), None)
    if not t:
        raise HTTPException(404, "Test type not found")
    t.update(req.model_dump(exclude_none=True))
    return t

@router.delete("/types/{type_id}", dependencies=[Depends(require_admin)])
def delete_test_type(type_id: str):
    t = next((x for x in lab_test_types_db if x["id"] == type_id), None)
    if not t:
        raise HTTPException(404, "Test type not found")
    lab_test_types_db[:] = [x for x in lab_test_types_db if x["id"] != type_id]
    return {"message": "Deleted"}

# ── Bookings ───────────────────────────────────────────────────────────────────
@router.get("/bookings")
def list_bookings(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "admin":
        return [_enrich_booking(b) for b in lab_bookings_db]
    return [_enrich_booking(b) for b in lab_bookings_db if b["patient_id"] == current_user["id"]]

@router.post("/bookings")
def book_test(req: LabBookingCreate, current_user: dict = Depends(get_current_user)):
    test_type = next((t for t in lab_test_types_db if t["id"] == req.test_type_id), None)
    if not test_type:
        raise HTTPException(404, "Test type not found")

    booking = {
        "id": next_id("lab_booking"),
        "patient_id": current_user["id"],
        "test_type_id": req.test_type_id,
        "appointment_id": req.appointment_id,
        "status": "booked",
        "booked_at": datetime.utcnow().isoformat(),
        "sample_collected_at": None,
        "payment_status": "pending",
        "amount": test_type["price"],
        "notes": req.notes or "",
    }
    lab_bookings_db.append(booking)
    return _enrich_booking(booking)

@router.put("/bookings/{booking_id}", dependencies=[Depends(require_admin)])
def update_booking_status(booking_id: str, req: LabBookingStatusUpdate, background_tasks: BackgroundTasks):
    b = next((x for x in lab_bookings_db if x["id"] == booking_id), None)
    if not b:
        raise HTTPException(404, "Booking not found")

    b["status"] = req.status
    if req.payment_status:
        b["payment_status"] = req.payment_status
    if req.status == "sample_collected":
        b["sample_collected_at"] = datetime.utcnow().isoformat()
    if req.status == "report_ready":
        test_type = next((t for t in lab_test_types_db if t["id"] == b["test_type_id"]), None)
        test_name = test_type["name"] if test_type else "Lab"
        background_tasks.add_task(_notify_report, b["patient_id"], test_name)

    return _enrich_booking(b)

@router.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: str, current_user: dict = Depends(get_current_user)):
    b = next((x for x in lab_bookings_db if x["id"] == booking_id), None)
    if not b:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] != "admin" and b["patient_id"] != current_user["id"]:
        raise HTTPException(403, "Not authorized")
    b["status"] = "cancelled"
    return {"message": "Booking cancelled"}
