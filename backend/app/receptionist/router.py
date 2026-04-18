"""Receptionist Portal — department-scoped: each receptionist sees only their specialization."""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

from app.mock_data import (
    appointments_db, doctors_db, specializations_db,
    payments_db, notifications_db, users_db, queue_state_db,
    prescriptions_db, next_id, queue_history_db,
)
from app.dependencies import require_receptionist
from app.payments.router import CONSULTATION_FEES

router = APIRouter(prefix="/receptionist", tags=["Receptionist"])


# ── Schemas ────────────────────────────────────────────────────────────────────
class WalkInPatient(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class WalkInBooking(BaseModel):
    patient_id: Optional[str] = None
    patient: Optional[WalkInPatient] = None
    doctor_id: str
    time_slot: str
    date: str
    notes: Optional[str] = ""
    payment_method: str = "cash"

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None

class StatusUpdate(BaseModel):
    status: str  # waiting | in_progress | completed | cancelled

class MedicineItem(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str
    instructions: Optional[str] = ""

class PrescriptionCreate(BaseModel):
    appointment_id: Optional[str] = None
    diagnosis: str
    medicines: list[MedicineItem]
    notes: Optional[str] = ""
    follow_up_date: Optional[str] = None

class PrescriptionUpdate(BaseModel):
    diagnosis: Optional[str] = None
    medicines: Optional[list[MedicineItem]] = None
    notes: Optional[str] = None
    follow_up_date: Optional[str] = None


# ── Helpers ────────────────────────────────────────────────────────────────────
def _safe(user: dict) -> dict:
    return {k: v for k, v in user.items() if k != "password_hash"}

def _enrich(apt: dict) -> dict:
    doctor  = next((d for d in doctors_db if d["id"] == apt["doctor_id"]), None)
    spec    = next((s for s in specializations_db if s["id"] == apt.get("specialization_id")), None)
    patient = next((u for u in users_db if u["id"] == apt["patient_id"]), None)
    return {**apt, "doctor": doctor, "specialization": spec,
            "patient": _safe(patient) if patient else None}

def _dept_doctors(spec_id: str) -> list:
    """All doctors in the receptionist's department."""
    if not spec_id:
        return []
    return [d for d in doctors_db if d.get("specialization_id") == spec_id]

def _dept_doctor_ids(spec_id: str) -> set:
    return {d["id"] for d in _dept_doctors(spec_id)}

def _dept_patient_ids(spec_id: str) -> set:
    """Unique patient IDs who have ever had an appointment in this department."""
    doc_ids = _dept_doctor_ids(spec_id)
    return {a["patient_id"] for a in appointments_db if a.get("doctor_id") in doc_ids}

def _avg_consult_minutes(doctor_id: str) -> int:
    history = [h for h in queue_history_db if h["doctor_id"] == doctor_id and h.get("patients_ahead", 0) > 0]
    if not history:
        return 15
    per_patient = [h["actual_wait_minutes"] / h["patients_ahead"] for h in history]
    return max(5, round(sum(per_patient) / len(per_patient)))

def _patients_ahead_priority(apt: dict, waiting: list) -> int:
    if apt["status"] != "waiting":
        return 0
    is_prio = apt.get("priority", False)
    return sum(
        1 for w in waiting
        if w["id"] != apt["id"] and (
            w.get("priority", False) or (not is_prio and w["token_number"] < apt["token_number"])
        )
    ) if not is_prio else sum(
        1 for w in waiting
        if w["id"] != apt["id"] and w.get("priority", False) and w["token_number"] < apt["token_number"]
    )

def _sort_queue(apts: list) -> list:
    """Sort: in_progress first, then priority waiting, then normal waiting, then completed."""
    order = {"in_progress": 0, "waiting": 1, "completed": 2, "cancelled": 3}
    return sorted(apts, key=lambda a: (
        order.get(a["status"], 9),
        not a.get("priority", False),   # priority first within waiting
        a["token_number"]
    ))


# ── My Department ─────────────────────────────────────────────────────────────
@router.get("/me")
def get_my_dept(current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    spec = next((s for s in specializations_db if s["id"] == spec_id), None)
    doctors = _dept_doctors(spec_id)
    return {
        "receptionist": _safe(current_user),
        "department": spec,
        "doctors": doctors,
    }


# ── Dashboard ─────────────────────────────────────────────────────────────────
@router.get("/dashboard")
def dashboard(current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    today   = date.today().isoformat()
    doc_ids = _dept_doctor_ids(spec_id)

    today_apts = [a for a in appointments_db
                  if a["date"] == today and a.get("doctor_id") in doc_ids]

    spec = next((s for s in specializations_db if s["id"] == spec_id), None)

    return {
        "today": today,
        "department": spec["name"] if spec else "All",
        "total_today":    len([a for a in today_apts if a["status"] != "cancelled"]),
        "waiting":        len([a for a in today_apts if a["status"] == "waiting"]),
        "in_progress":    len([a for a in today_apts if a["status"] == "in_progress"]),
        "completed":      len([a for a in today_apts if a["status"] == "completed"]),
        "total_patients": len(_dept_patient_ids(spec_id)),
        "doctors_in_dept": len(doc_ids),
    }


# ── Patients (dept-scoped) ────────────────────────────────────────────────────
@router.get("/patients")
def list_patients(search: Optional[str] = None,
                  current_user: dict = Depends(require_receptionist)):
    spec_id    = current_user.get("specialization_id")
    patient_ids = _dept_patient_ids(spec_id)
    patients   = [u for u in users_db if u.get("role") == "patient" and u["id"] in patient_ids]

    if search:
        s = search.lower()
        patients = [p for p in patients if
                    s in p["name"].lower()
                    or (p.get("email") and s in p["email"].lower())
                    or (p.get("phone") and s in (p["phone"] or ""))]
    return [_safe(p) for p in patients]


# ── Edit Patient Details ──────────────────────────────────────────────────────
@router.put("/patients/{patient_id}")
def update_patient(patient_id: str, req: PatientUpdate,
                   current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    if patient_id not in _dept_patient_ids(spec_id):
        raise HTTPException(403, "Patient not in your department")
    patient = next((u for u in users_db if u["id"] == patient_id), None)
    if not patient:
        raise HTTPException(404, "Patient not found")
    for field, val in req.model_dump(exclude_none=True).items():
        patient[field] = val
    return _safe(patient)


# ── Register Walk-in Patient ──────────────────────────────────────────────────
@router.post("/register-patient")
def register_patient(req: WalkInPatient,
                     current_user: dict = Depends(require_receptionist)):
    pid = next_id("user")
    patient = {
        "id": pid,
        "name": req.name,
        "email": req.email or f"walkin_{pid}@hospital.local",
        "password_hash": "plain:walkin",
        "role": "patient",
        "hospital_id": current_user.get("hospital_id", "h1"),
        "doctor_id": None,
        "phone": req.phone,
        "age": req.age,
        "gender": req.gender,
        "walk_in": True,
        "created_at": datetime.utcnow().isoformat(),
    }
    users_db.append(patient)
    return _safe(patient)


# ── Book Appointment (dept-scoped) ────────────────────────────────────────────
@router.post("/book")
def book_for_patient(req: WalkInBooking, bg: BackgroundTasks,
                     current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")

    # Verify doctor belongs to this department
    doctor = next((d for d in doctors_db if d["id"] == req.doctor_id), None)
    if not doctor or doctor.get("specialization_id") != spec_id:
        raise HTTPException(403, "Doctor is not in your department")

    # Resolve patient
    if req.patient_id:
        patient = next((u for u in users_db if u["id"] == req.patient_id), None)
        if not patient:
            raise HTTPException(404, "Patient not found")
        patient_id = req.patient_id
    elif req.patient:
        pid = next_id("user")
        patient = {
            "id": pid,
            "name": req.patient.name,
            "email": req.patient.email or f"walkin_{pid}@hospital.local",
            "password_hash": "plain:walkin",
            "role": "patient",
            "hospital_id": current_user.get("hospital_id", "h1"),
            "doctor_id": None,
            "phone": req.patient.phone,
            "age": req.patient.age,
            "gender": req.patient.gender,
            "walk_in": True,
            "created_at": datetime.utcnow().isoformat(),
        }
        users_db.append(patient)
        patient_id = pid
    else:
        raise HTTPException(400, "Provide patient_id or patient details")

    # Slot conflict
    conflict = next((a for a in appointments_db
                     if a["doctor_id"] == req.doctor_id and a["date"] == req.date
                     and a["time_slot"] == req.time_slot and a["status"] != "cancelled"), None)
    if conflict:
        raise HTTPException(400, "This time slot is already booked")

    day_apts = [a for a in appointments_db
                if a["doctor_id"] == req.doctor_id and a["date"] == req.date
                and a["status"] != "cancelled"]
    token_number = len(day_apts) + 1

    apt = {
        "id": next_id("appointment"),
        "patient_id": patient_id,
        "doctor_id": req.doctor_id,
        "specialization_id": spec_id,
        "date": req.date,
        "time_slot": req.time_slot,
        "token_number": token_number,
        "status": "waiting",
        "priority": False,
        "notes": req.notes or "",
        "booked_by": current_user["id"],
        "booked_by_role": current_user["role"],
    }
    appointments_db.append(apt)

    key = f"{req.doctor_id}:{req.date}"
    if key not in queue_state_db:
        queue_state_db[key] = {"current_token": 0, "doctor_id": req.doctor_id, "date": req.date}

    # Record payment
    fee = CONSULTATION_FEES.get(spec_id, 300)
    payment = {
        "id": next_id("payment"),
        "appointment_id": apt["id"],
        "patient_id": patient_id,
        "amount": fee,
        "currency": "INR",
        "status": "paid" if req.payment_method in ("cash", "upi") else "pending",
        "razorpay_order_id": f"walkin_{apt['id']}",
        "razorpay_payment_id": f"{req.payment_method}_{apt['id']}",
        "method": req.payment_method,
        "created_at": datetime.utcnow().isoformat(),
    }
    payments_db.append(payment)

    if patient.get("phone") or patient.get("email"):
        bg.add_task(_notify_walkin, patient_id, apt, fee, req.payment_method)

    return {
        "appointment":  _enrich(apt),
        "payment":      payment,
        "token_number": token_number,
        "patient":      _safe(patient),
    }


# ── Queue Overview (dept-scoped summary) ──────────────────────────────────────
@router.get("/queue-overview")
def queue_overview(current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    today   = date.today().isoformat()
    result  = []
    spec_name = next((s["name"] for s in specializations_db if s["id"] == spec_id), "")
    for doc in _dept_doctors(spec_id):
        apts = [a for a in appointments_db
                if a.get("doctor_id") == doc["id"] and a["date"] == today
                and a["status"] != "cancelled"]
        q = queue_state_db.get(f"{doc['id']}:{today}", {"current_token": 0})
        result.append({
            "doctor_id":      doc["id"],
            "doctor_name":    doc["name"],
            "specialization": spec_name,
            "current_token":  q.get("current_token", 0),
            "total":          len(apts),
            "waiting":        len([a for a in apts if a["status"] == "waiting"]),
            "in_progress":    len([a for a in apts if a["status"] == "in_progress"]),
            "completed":      len([a for a in apts if a["status"] == "completed"]),
            "priority_count": len([a for a in apts if a.get("priority") and a["status"] == "waiting"]),
        })
    return result


# ── Today's Appointments (dept-scoped) ───────────────────────────────────────
@router.get("/appointments/today")
def today_appointments(current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    today   = date.today().isoformat()
    doc_ids = _dept_doctor_ids(spec_id)
    apts = [a for a in appointments_db
            if a["date"] == today and a.get("doctor_id") in doc_ids]
    return [_enrich(a) for a in sorted(apts, key=lambda a: a["token_number"])]


# ── Doctors in dept (for booking dropdown) ────────────────────────────────────
@router.get("/doctors")
def dept_doctors(current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    return _dept_doctors(spec_id)


# ── Full Queue Detail for a Doctor (dept-scoped) ──────────────────────────────
@router.get("/queue/{doctor_id}")
def get_doctor_queue(doctor_id: str, current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    doctor  = next((d for d in doctors_db if d["id"] == doctor_id), None)
    if not doctor or doctor.get("specialization_id") != spec_id:
        raise HTTPException(403, "Doctor not in your department")
    today = date.today().isoformat()
    key   = f"{doctor_id}:{today}"
    state = queue_state_db.get(key, {"current_token": 0})
    apts  = [a for a in appointments_db
             if a.get("doctor_id") == doctor_id and a["date"] == today
             and a["status"] != "cancelled"]
    current = state.get("current_token", 0)
    avg_min = _avg_consult_minutes(doctor_id)
    waiting = [a for a in apts if a["status"] == "waiting"]
    in_progress = next((a for a in apts if a["status"] == "in_progress"), None)
    enriched = []
    for a in _sort_queue(apts):
        e = _enrich(a)
        ahead = _patients_ahead_priority(a, waiting)
        e["patients_ahead"] = ahead
        in_prog_buffer = (avg_min // 2) if in_progress and a["status"] == "waiting" else 0
        e["estimated_wait_minutes"] = (ahead * avg_min + in_prog_buffer) if a["status"] == "waiting" else 0
        e["avg_consult_minutes"] = avg_min
        enriched.append(e)
    return {
        "doctor_id":           doctor_id,
        "doctor_name":         doctor["name"],
        "current_token":       current,
        "total":               len(apts),
        "avg_consult_minutes": avg_min,
        "appointments":        enriched,
    }


# ── Call Next Patient (priority-aware) ────────────────────────────────────────
@router.post("/queue/{doctor_id}/next")
def next_patient(doctor_id: str, current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    doctor  = next((d for d in doctors_db if d["id"] == doctor_id), None)
    if not doctor or doctor.get("specialization_id") != spec_id:
        raise HTTPException(403, "Doctor not in your department")
    today = date.today().isoformat()
    key   = f"{doctor_id}:{today}"
    if key not in queue_state_db:
        queue_state_db[key] = {"current_token": 0, "doctor_id": doctor_id, "date": today}

    # Complete current in-progress
    cur = next((a for a in appointments_db
                if a.get("doctor_id") == doctor_id and a["date"] == today
                and a["status"] == "in_progress"), None)
    if cur:
        cur["status"] = "completed"

    # Pick next: priority patients first, then by token number
    waiting = sorted(
        [a for a in appointments_db
         if a.get("doctor_id") == doctor_id and a["date"] == today and a["status"] == "waiting"],
        key=lambda x: (not x.get("priority", False), x["token_number"])
    )
    if not waiting:
        return {"current_token": queue_state_db[key].get("current_token", 0),
                "message": "No more patients waiting"}

    nxt = waiting[0]
    nxt["status"] = "in_progress"
    queue_state_db[key]["current_token"] = nxt["token_number"]
    name = next((u["name"] for u in users_db if u["id"] == nxt["patient_id"]), "Patient")
    priority_note = " [PRIORITY]" if nxt.get("priority") else ""
    return {
        "current_token": nxt["token_number"],
        "message": f"Now serving token #{nxt['token_number']} — {name}{priority_note}",
    }


# ── Update Appointment Status ─────────────────────────────────────────────────
@router.post("/appointments/{apt_id}/status")
def update_appointment_status(apt_id: str, req: StatusUpdate,
                              current_user: dict = Depends(require_receptionist)):
    valid_statuses = {"waiting", "in_progress", "completed", "cancelled"}
    if req.status not in valid_statuses:
        raise HTTPException(400, f"Invalid status. Must be one of {valid_statuses}")
    spec_id = current_user.get("specialization_id")
    doc_ids = _dept_doctor_ids(spec_id)
    apt = next((a for a in appointments_db if a["id"] == apt_id), None)
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if apt.get("doctor_id") not in doc_ids:
        raise HTTPException(403, "Appointment not in your department")
    apt["status"] = req.status
    return _enrich(apt)


# ── Toggle Priority ───────────────────────────────────────────────────────────
@router.post("/appointments/{apt_id}/priority")
def toggle_priority(apt_id: str, current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    doc_ids = _dept_doctor_ids(spec_id)
    apt = next((a for a in appointments_db if a["id"] == apt_id), None)
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if apt.get("doctor_id") not in doc_ids:
        raise HTTPException(403, "Appointment not in your department")
    apt["priority"] = not apt.get("priority", False)
    return {"priority": apt["priority"], "appointment": _enrich(apt)}


# ── All Prescriptions for dept ────────────────────────────────────────────────
@router.get("/prescriptions")
def list_all_prescriptions(search: Optional[str] = None,
                           current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    patient_ids = _dept_patient_ids(spec_id)
    doc_ids     = _dept_doctor_ids(spec_id)

    prescs = [p for p in prescriptions_db
              if p["patient_id"] in patient_ids]

    if search:
        s = search.lower()
        prescs = [p for p in prescs if
                  s in p.get("diagnosis", "").lower()
                  or s in p.get("doctor_name", "").lower()
                  or any(s in m.get("name", "").lower() for m in p.get("medicines", []))]

    enriched = []
    for p in sorted(prescs, key=lambda x: x["created_at"], reverse=True):
        patient = next((u for u in users_db if u["id"] == p["patient_id"]), None)
        enriched.append({**p, "patient": _safe(patient) if patient else None})
    return enriched


# ── Patient Detail (dept-scoped) ─────────────────────────────────────────────
@router.get("/patients/{patient_id}")
def get_patient_detail(patient_id: str, current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    if patient_id not in _dept_patient_ids(spec_id):
        raise HTTPException(403, "Patient not in your department")
    patient = next((u for u in users_db if u["id"] == patient_id), None)
    if not patient:
        raise HTTPException(404, "Patient not found")
    doc_ids = _dept_doctor_ids(spec_id)
    apt_history = sorted(
        [_enrich(a) for a in appointments_db
         if a["patient_id"] == patient_id and a.get("doctor_id") in doc_ids],
        key=lambda x: x["date"], reverse=True
    )
    prescriptions = [
        p for p in prescriptions_db
        if p["patient_id"] == patient_id and p.get("doctor_id") in doc_ids
    ]
    return {
        "patient": _safe(patient),
        "appointments": apt_history,
        "prescriptions": sorted(prescriptions, key=lambda x: x["created_at"], reverse=True),
    }


# ── Prescriptions for a Patient ───────────────────────────────────────────────
@router.get("/patients/{patient_id}/prescriptions")
def list_patient_prescriptions(patient_id: str, current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    if patient_id not in _dept_patient_ids(spec_id):
        raise HTTPException(403, "Patient not in your department")
    doc_ids = _dept_doctor_ids(spec_id)
    result = sorted(
        [p for p in prescriptions_db if p["patient_id"] == patient_id and p.get("doctor_id") in doc_ids],
        key=lambda x: x["created_at"], reverse=True
    )
    return result


@router.post("/patients/{patient_id}/prescriptions")
def add_prescription(patient_id: str, req: PrescriptionCreate, bg: BackgroundTasks,
                     current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    if patient_id not in _dept_patient_ids(spec_id):
        raise HTTPException(403, "Patient not in your department")

    # Determine which doctor to associate (use the appointment's doctor, or dept's first doctor)
    doctor_id = None
    doctor_name = "Receptionist"
    if req.appointment_id:
        apt = next((a for a in appointments_db if a["id"] == req.appointment_id), None)
        if apt:
            doctor_id = apt["doctor_id"]
            doc = next((d for d in doctors_db if d["id"] == doctor_id), None)
            if doc:
                doctor_name = doc["name"]

    presc = {
        "id": next_id("prescription"),
        "appointment_id": req.appointment_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "doctor_name": doctor_name,
        "created_by": current_user["id"],
        "created_by_role": "receptionist",
        "diagnosis": req.diagnosis,
        "medicines": [m.model_dump() for m in req.medicines],
        "notes": req.notes or "",
        "follow_up_date": req.follow_up_date,
        "hospital_id": current_user.get("hospital_id", "h1"),
        "created_at": datetime.utcnow().isoformat(),
        "file_url": None,
    }
    prescriptions_db.append(presc)
    bg.add_task(_notify_prescription, patient_id, doctor_name)
    if req.follow_up_date:
        bg.add_task(_notify_followup, patient_id, doctor_name, req.follow_up_date)
    return presc


# ── Update Prescription ───────────────────────────────────────────────────────
@router.put("/prescriptions/{presc_id}")
def update_prescription(presc_id: str, req: PrescriptionUpdate,
                        current_user: dict = Depends(require_receptionist)):
    spec_id = current_user.get("specialization_id")
    doc_ids = _dept_doctor_ids(spec_id)
    presc = next((p for p in prescriptions_db if p["id"] == presc_id), None)
    if not presc:
        raise HTTPException(404, "Prescription not found")
    if presc.get("doctor_id") not in doc_ids and presc.get("created_by") != current_user["id"]:
        raise HTTPException(403, "Prescription not in your department")
    updates = req.model_dump(exclude_none=True)
    if "medicines" in updates:
        updates["medicines"] = [m.model_dump() if hasattr(m, "model_dump") else m for m in req.medicines]
    presc.update(updates)
    return presc


# ── Background notification ───────────────────────────────────────────────────
def _notify_followup(patient_id: str, doctor_name: str, follow_up_date: str):
    try:
        from datetime import date as _date
        formatted = _date.fromisoformat(follow_up_date).strftime("%-d %B %Y")
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


def _notify_prescription(patient_id: str, doctor_name: str):
    notifications_db.append({
        "id": next_id("notification"),
        "user_id": patient_id,
        "type": "prescription",
        "title": "New Prescription Added",
        "message": f"A prescription from {doctor_name} has been added to your profile.",
        "read": False,
        "action_url": "/patient/prescriptions",
        "created_at": datetime.utcnow().isoformat(),
    })

def _notify_walkin(patient_id: str, apt: dict, fee: float, payment_method: str):
    doctor = next((d for d in doctors_db if d["id"] == apt["doctor_id"]), None)
    notifications_db.append({
        "id": next_id("notification"),
        "user_id": patient_id,
        "type": "appointment",
        "title": "Appointment Booked",
        "message": (f"Your appointment with {doctor['name'] if doctor else 'Doctor'} "
                    f"on {apt['date']} at {apt['time_slot']} is confirmed. "
                    f"Token #{apt['token_number']}. Payment: ₹{fee:.0f} ({payment_method.upper()})."),
        "read": False,
        "action_url": "/patient/appointments",
        "created_at": datetime.utcnow().isoformat(),
    })
