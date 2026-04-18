"""Doctor Portal — self-service endpoints for logged-in doctors."""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.mock_data import (
    appointments_db, doctors_db, specializations_db,
    prescriptions_db, notifications_db, queue_state_db,
    users_db, next_id,
)
from app.dependencies import require_doctor
from app.websocket_manager import manager

router = APIRouter(prefix="/doctor", tags=["Doctor Portal"])


# ── Helpers ────────────────────────────────────────────────────────────────────
def _enrich_apt(apt: dict) -> dict:
    doctor = next((d for d in doctors_db if d["id"] == apt["doctor_id"]), None)
    spec   = next((s for s in specializations_db if s["id"] == apt["specialization_id"]), None)
    patient = next((u for u in users_db if u["id"] == apt["patient_id"]), None)
    patient_safe = {k: v for k, v in patient.items() if k != "password_hash"} if patient else None
    return {**apt, "doctor": doctor, "specialization": spec, "patient": patient_safe}

async def _broadcast_queue(doctor_id: str, target_date: str):
    apts = [a for a in appointments_db if a["doctor_id"] == doctor_id and a["date"] == target_date]
    q_state = queue_state_db.get(f"{doctor_id}:{target_date}", {"current_token": 0})
    await manager.broadcast(doctor_id, {
        "type": "queue_update",
        "doctor_id": doctor_id,
        "current_token": q_state.get("current_token", 0),
        "total_patients": len([a for a in apts if a["status"] != "cancelled"]),
        "waiting":    len([a for a in apts if a["status"] == "waiting"]),
        "in_progress":len([a for a in apts if a["status"] == "in_progress"]),
        "completed":  len([a for a in apts if a["status"] == "completed"]),
    })


# ── Schemas ────────────────────────────────────────────────────────────────────
class MedicineItem(BaseModel):
    name: str; dosage: str = ""; frequency: str = ""
    duration: str = ""; instructions: str = ""

class PrescriptionWrite(BaseModel):
    appointment_id: str
    patient_id: str
    diagnosis: str
    medicines: List[MedicineItem]
    notes: str = ""
    follow_up_date: Optional[str] = None

class AppointmentNote(BaseModel):
    notes: Optional[str] = None
    status: Optional[str] = None


# ── Profile ────────────────────────────────────────────────────────────────────
@router.get("/me")
def get_my_profile(current_user: dict = Depends(require_doctor)):
    doctor_id = current_user.get("doctor_id")
    doctor = next((d for d in doctors_db if d["id"] == doctor_id), None)
    return {"user": {k: v for k, v in current_user.items() if k != "password_hash"}, "doctor": doctor}


# ── Appointments ───────────────────────────────────────────────────────────────
@router.get("/appointments")
def get_my_appointments(current_user: dict = Depends(require_doctor)):
    doctor_id = current_user.get("doctor_id")
    apts = [a for a in appointments_db if a["doctor_id"] == doctor_id]
    return [_enrich_apt(a) for a in apts]

@router.get("/appointments/today")
def get_today_appointments(current_user: dict = Depends(require_doctor)):
    doctor_id = current_user.get("doctor_id")
    today = date.today().isoformat()
    apts  = [a for a in appointments_db if a["doctor_id"] == doctor_id and a["date"] == today]
    return [_enrich_apt(a) for a in sorted(apts, key=lambda a: a["token_number"])]

@router.get("/queue")
def get_my_queue(current_user: dict = Depends(require_doctor)):
    doctor_id = current_user.get("doctor_id")
    today     = date.today().isoformat()
    apts      = [a for a in appointments_db if a["doctor_id"] == doctor_id and a["date"] == today and a["status"] != "cancelled"]
    q_state   = queue_state_db.get(f"{doctor_id}:{today}", {"current_token": 0})
    return {
        "doctor_id": doctor_id,
        "date": today,
        "current_token": q_state.get("current_token", 0),
        "total_patients": len(apts),
        "waiting":     len([a for a in apts if a["status"] == "waiting"]),
        "in_progress": len([a for a in apts if a["status"] == "in_progress"]),
        "completed":   len([a for a in apts if a["status"] == "completed"]),
        "appointments": [_enrich_apt(a) for a in sorted(apts, key=lambda a: a["token_number"])],
    }


# ── Queue Actions (with WebSocket broadcast) ───────────────────────────────────
@router.post("/appointments/{apt_id}/start")
async def start_patient(apt_id: str, current_user: dict = Depends(require_doctor)):
    apt = next((a for a in appointments_db if a["id"] == apt_id), None)
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if apt["doctor_id"] != current_user.get("doctor_id"):
        raise HTTPException(403, "Not your appointment")
    apt["status"] = "in_progress"
    today = date.today().isoformat()
    key   = f"{apt['doctor_id']}:{today}"
    if key in queue_state_db:
        queue_state_db[key]["current_token"] = apt["token_number"]
    await _broadcast_queue(apt["doctor_id"], today)
    return _enrich_apt(apt)

@router.post("/appointments/{apt_id}/complete")
async def complete_patient(apt_id: str, bg: BackgroundTasks,
                           current_user: dict = Depends(require_doctor)):
    apt = next((a for a in appointments_db if a["id"] == apt_id), None)
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if apt["doctor_id"] != current_user.get("doctor_id"):
        raise HTTPException(403, "Not your appointment")
    apt["status"] = "completed"
    today = date.today().isoformat()
    await _broadcast_queue(apt["doctor_id"], today)
    # Notify patient
    bg.add_task(_notify_complete, apt["patient_id"], apt["doctor_id"])
    return _enrich_apt(apt)

@router.post("/appointments/{apt_id}/skip")
async def skip_patient(apt_id: str, current_user: dict = Depends(require_doctor)):
    apt = next((a for a in appointments_db if a["id"] == apt_id), None)
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if apt["doctor_id"] != current_user.get("doctor_id"):
        raise HTTPException(403, "Not your appointment")
    apt["status"] = "skipped"
    today = date.today().isoformat()
    await _broadcast_queue(apt["doctor_id"], today)
    return _enrich_apt(apt)

@router.put("/appointments/{apt_id}/notes")
def update_notes(apt_id: str, req: AppointmentNote, current_user: dict = Depends(require_doctor)):
    apt = next((a for a in appointments_db if a["id"] == apt_id), None)
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if apt["doctor_id"] != current_user.get("doctor_id"):
        raise HTTPException(403, "Not your appointment")
    if req.notes is not None:
        apt["notes"] = req.notes
    return _enrich_apt(apt)


# ── Prescriptions ──────────────────────────────────────────────────────────────
@router.post("/appointments/{apt_id}/prescribe-complete")
async def prescribe_and_complete(apt_id: str, req: PrescriptionWrite, bg: BackgroundTasks,
                                  current_user: dict = Depends(require_doctor)):
    """Write prescription and mark appointment complete in one action."""
    apt = next((a for a in appointments_db if a["id"] == apt_id), None)
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if apt["doctor_id"] != current_user.get("doctor_id"):
        raise HTTPException(403, "Not your appointment")

    doctor_id = current_user.get("doctor_id")
    doctor    = next((d for d in doctors_db if d["id"] == doctor_id), None)

    # Write prescription
    presc = {
        "id": next_id("prescription"),
        "appointment_id": apt_id,
        "patient_id": req.patient_id,
        "doctor_id": doctor_id,
        "doctor_name": doctor["name"] if doctor else current_user["name"],
        "diagnosis": req.diagnosis,
        "medicines": [m.model_dump() for m in req.medicines],
        "notes": req.notes,
        "follow_up_date": req.follow_up_date,
        "file_url": None,
        "created_at": datetime.utcnow().isoformat(),
        "hospital_id": current_user.get("hospital_id", "h1"),
    }
    prescriptions_db.append(presc)

    # Mark appointment complete
    apt["status"] = "completed"
    today = date.today().isoformat()
    await _broadcast_queue(doctor_id, today)
    bg.add_task(_notify_prescription, req.patient_id, doctor["name"] if doctor else "Doctor",
                req.diagnosis or "", req.follow_up_date)
    if req.follow_up_date:
        bg.add_task(_notify_followup_reminder, req.patient_id,
                    doctor["name"] if doctor else "Doctor", req.follow_up_date)
    bg.add_task(_notify_complete, req.patient_id, doctor_id)

    return {"prescription": presc, "appointment": _enrich_apt(apt)}


@router.get("/prescriptions")
def get_my_prescriptions(current_user: dict = Depends(require_doctor)):
    doctor_id = current_user.get("doctor_id")
    return [p for p in prescriptions_db if p["doctor_id"] == doctor_id]

@router.post("/prescriptions")
def write_prescription(req: PrescriptionWrite, bg: BackgroundTasks,
                       current_user: dict = Depends(require_doctor)):
    doctor_id = current_user.get("doctor_id")
    doctor    = next((d for d in doctors_db if d["id"] == doctor_id), None)
    presc = {
        "id": next_id("prescription"),
        "appointment_id": req.appointment_id,
        "patient_id": req.patient_id,
        "doctor_id": doctor_id,
        "doctor_name": doctor["name"] if doctor else current_user["name"],
        "diagnosis": req.diagnosis,
        "medicines": [m.model_dump() for m in req.medicines],
        "notes": req.notes,
        "follow_up_date": req.follow_up_date,
        "file_url": None,
        "created_at": datetime.utcnow().isoformat(),
        "hospital_id": current_user.get("hospital_id", "h1"),
    }
    prescriptions_db.append(presc)
    bg.add_task(_notify_prescription, req.patient_id, doctor["name"] if doctor else "Doctor",
                req.diagnosis or "", req.follow_up_date)
    if req.follow_up_date:
        bg.add_task(_notify_followup_reminder, req.patient_id,
                    doctor["name"] if doctor else "Doctor", req.follow_up_date)
    return presc


# ── Patients list ──────────────────────────────────────────────────────────────
@router.get("/patients")
def get_my_patients(current_user: dict = Depends(require_doctor)):
    doctor_id = current_user.get("doctor_id")
    patient_ids = list({a["patient_id"] for a in appointments_db if a["doctor_id"] == doctor_id})
    patients = []
    for pid in patient_ids:
        user = next((u for u in users_db if u["id"] == pid), None)
        if user:
            pt_apts = [a for a in appointments_db if a["doctor_id"] == doctor_id and a["patient_id"] == pid]
            patients.append({
                "id": pid,
                "name": user["name"],
                "email": user["email"],
                "total_visits": len(pt_apts),
                "last_visit": max((a["date"] for a in pt_apts), default=None),
            })
    return sorted(patients, key=lambda p: p["last_visit"] or "", reverse=True)


# ── Background notification tasks ──────────────────────────────────────────────
def _notify_complete(patient_id: str, doctor_id: str):
    doctor = next((d for d in doctors_db if d["id"] == doctor_id), None)
    doctor_name = doctor["name"] if doctor else "your doctor"
    notifications_db.append({
        "id": next_id("notification"),
        "user_id": patient_id,
        "type": "appointment",
        "title": "Consultation Complete",
        "message": f"Your consultation with {doctor_name} is complete. Prescription is ready.",
        "read": False,
        "action_url": "/patient/prescriptions",
        "created_at": datetime.utcnow().isoformat(),
    })


def _notify_followup_reminder(patient_id: str, doctor_name: str, follow_up_date: str):
    """Create a follow-up reminder notification for the patient."""
    try:
        from datetime import date as _date
        fu = _date.fromisoformat(follow_up_date)
        formatted = fu.strftime("%-d %B %Y")
    except Exception:
        formatted = follow_up_date
    notifications_db.append({
        "id": next_id("notification"),
        "user_id": patient_id,
        "type": "follow_up",
        "title": "Follow-up Appointment Reminder",
        "message": f"Dr. {doctor_name} has scheduled a follow-up for you on {formatted}. Please book your appointment.",
        "read": False,
        "action_url": "/patient/appointments",
        "created_at": datetime.utcnow().isoformat(),
    })
    user = next((u for u in users_db if u["id"] == patient_id), None)
    if user and user.get("phone"):
        try:
            from app.whatsapp_service import send_whatsapp
            send_whatsapp(
                phone=user["phone"],
                message=(f"Hi {user.get('name','Patient')}, Dr. {doctor_name} has scheduled your "
                         f"follow-up appointment on {formatted}. Please visit the hospital or book online.")
            )
        except Exception:
            pass


def _notify_prescription(patient_id: str, doctor_name: str, diagnosis: str = "",
                          follow_up: str = None):
    msg = f"Dr. {doctor_name} has issued a prescription for you."
    if diagnosis:
        msg += f" Diagnosis: {diagnosis}."
    notifications_db.append({
        "id": next_id("notification"),
        "user_id": patient_id,
        "type": "prescription",
        "title": "New Prescription",
        "message": msg,
        "read": False,
        "action_url": "/patient/prescriptions",
        "created_at": datetime.utcnow().isoformat(),
    })
    # Send WhatsApp
    user = next((u for u in users_db if u["id"] == patient_id), None)
    if user and user.get("phone"):
        from app.whatsapp_service import wa_prescription_ready
        wa_prescription_ready(
            phone=user["phone"],
            patient_name=user.get("name", "Patient"),
            doctor_name=doctor_name,
            diagnosis=diagnosis,
            follow_up=follow_up,
        )
