"""Doctor Portal — self-service endpoints for logged-in doctors (database-backed)."""
import uuid
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Appointment, Doctor, Specialization, User,
    Prescription, PrescriptionMedicine, Notification, QueueState,
)
from app.dependencies import require_doctor
from app.websocket_manager import manager

router = APIRouter(prefix="/doctor", tags=["Doctor Portal"])


# ── Helpers ────────────────────────────────────────────────────────────────────
def _enrich_apt(apt: Appointment, db: Session) -> dict:
    d = apt.to_dict()
    doctor  = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first()
    spec    = db.query(Specialization).filter(Specialization.id == apt.specialization_id).first()
    patient = db.query(User).filter(User.id == apt.patient_id).first()
    d["doctor"]         = doctor.to_dict() if doctor else None
    d["specialization"] = spec.to_dict() if spec else None
    d["patient"]        = patient.safe_dict() if patient else None
    return d


async def _broadcast_queue(doctor_id: str, target_date: str, db: Session):
    apts = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == target_date,
        Appointment.status != "cancelled",
    ).all()
    q_state = db.query(QueueState).filter(
        QueueState.id == f"{doctor_id}:{target_date}"
    ).first()
    await manager.broadcast(doctor_id, {
        "type": "queue_update",
        "doctor_id": doctor_id,
        "current_token": q_state.current_token if q_state else 0,
        "total_patients": len(apts),
        "waiting":     len([a for a in apts if a.status == "waiting"]),
        "in_progress": len([a for a in apts if a.status == "in_progress"]),
        "completed":   len([a for a in apts if a.status == "completed"]),
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
def get_my_profile(current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == current_user.get("doctor_id")).first()
    return {"user": {k: v for k, v in current_user.items() if k != "password_hash"}, "doctor": doctor.to_dict() if doctor else None}


# ── Appointments ───────────────────────────────────────────────────────────────
@router.get("/appointments")
def get_my_appointments(current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    doctor_id = current_user.get("doctor_id")
    apts = db.query(Appointment).filter(Appointment.doctor_id == doctor_id).order_by(Appointment.date, Appointment.token_number).all()
    return [_enrich_apt(a, db) for a in apts]


@router.get("/appointments/range")
def get_appointments_range(current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    """Return appointments for today + next 3 days."""
    doctor_id = current_user.get("doctor_id")
    today = date.today()
    end   = today + timedelta(days=3)
    apts  = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date >= today.isoformat(),
        Appointment.date <= end.isoformat(),
    ).order_by(Appointment.date, Appointment.token_number).all()
    return [_enrich_apt(a, db) for a in apts]


@router.get("/appointments/today")
def get_today_appointments(current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    doctor_id = current_user.get("doctor_id")
    today = date.today().isoformat()
    apts  = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == today,
    ).order_by(Appointment.token_number).all()
    return [_enrich_apt(a, db) for a in apts]


@router.get("/queue")
def get_my_queue(current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    doctor_id = current_user.get("doctor_id")
    today     = date.today().isoformat()
    apts      = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == today,
        Appointment.status != "cancelled",
    ).order_by(Appointment.token_number).all()
    q_state = db.query(QueueState).filter(QueueState.id == f"{doctor_id}:{today}").first()
    return {
        "doctor_id": doctor_id,
        "date": today,
        "current_token": q_state.current_token if q_state else 0,
        "total_patients": len(apts),
        "waiting":     len([a for a in apts if a.status == "waiting"]),
        "in_progress": len([a for a in apts if a.status == "in_progress"]),
        "completed":   len([a for a in apts if a.status == "completed"]),
        "appointments": [_enrich_apt(a, db) for a in apts],
    }


# ── Queue Actions ──────────────────────────────────────────────────────────────
@router.post("/appointments/{apt_id}/start")
async def start_patient(apt_id: str, current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if apt.doctor_id != current_user.get("doctor_id"):
        raise HTTPException(403, "Not your appointment")
    apt.status = "in_progress"
    q_state = db.query(QueueState).filter(QueueState.id == f"{apt.doctor_id}:{apt.date}").first()
    if q_state:
        q_state.current_token = apt.token_number
    db.commit()
    await _broadcast_queue(apt.doctor_id, apt.date, db)
    return _enrich_apt(apt, db)


@router.post("/appointments/{apt_id}/complete")
async def complete_patient(apt_id: str, bg: BackgroundTasks,
                           current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if apt.doctor_id != current_user.get("doctor_id"):
        raise HTTPException(403, "Not your appointment")
    apt.status = "completed"
    db.commit()
    await _broadcast_queue(apt.doctor_id, apt.date, db)
    bg.add_task(_notify_complete, apt.patient_id, apt.doctor_id)
    return _enrich_apt(apt, db)


@router.post("/appointments/{apt_id}/skip")
async def skip_patient(apt_id: str, current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if apt.doctor_id != current_user.get("doctor_id"):
        raise HTTPException(403, "Not your appointment")
    apt.status = "skipped"
    db.commit()
    await _broadcast_queue(apt.doctor_id, apt.date, db)
    return _enrich_apt(apt, db)


@router.put("/appointments/{apt_id}/notes")
def update_notes(apt_id: str, req: AppointmentNote,
                 current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if apt.doctor_id != current_user.get("doctor_id"):
        raise HTTPException(403, "Not your appointment")
    if req.notes is not None:
        apt.notes = req.notes
    db.commit()
    return _enrich_apt(apt, db)


# ── Prescriptions ──────────────────────────────────────────────────────────────
@router.post("/appointments/{apt_id}/prescribe-complete")
async def prescribe_and_complete(apt_id: str, req: PrescriptionWrite, bg: BackgroundTasks,
                                  current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if apt.doctor_id != current_user.get("doctor_id"):
        raise HTTPException(403, "Not your appointment")

    doctor = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first()
    doctor_name = doctor.name if doctor else current_user.get("name", "Doctor")

    presc = Prescription(
        id=str(uuid.uuid4())[:50],
        appointment_id=apt_id,
        patient_id=req.patient_id,
        doctor_id=apt.doctor_id,
        doctor_name=doctor_name,
        diagnosis=req.diagnosis,
        notes=req.notes,
        follow_up_date=req.follow_up_date,
        file_url=None,
        created_at=datetime.utcnow().isoformat(),
        hospital_id=current_user.get("hospital_id", "h1"),
    )
    db.add(presc)

    for m in req.medicines:
        db.add(PrescriptionMedicine(
            prescription_id=presc.id,
            name=m.name,
            dosage=m.dosage,
            frequency=m.frequency,
            duration=m.duration,
            instructions=m.instructions,
        ))

    apt.status = "completed"
    db.commit()
    db.refresh(presc)

    await _broadcast_queue(apt.doctor_id, apt.date, db)
    bg.add_task(_notify_prescription, req.patient_id, doctor_name, req.diagnosis, req.follow_up_date)
    if req.follow_up_date:
        bg.add_task(_notify_followup_reminder, req.patient_id, doctor_name, req.follow_up_date)
    bg.add_task(_notify_complete, req.patient_id, apt.doctor_id)

    return {"prescription": presc.to_dict(), "appointment": _enrich_apt(apt, db)}


@router.get("/prescriptions")
def get_my_prescriptions(current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    doctor_id = current_user.get("doctor_id")
    prescs = db.query(Prescription).filter(Prescription.doctor_id == doctor_id).order_by(Prescription.created_at.desc()).all()
    return [p.to_dict() for p in prescs]


@router.post("/prescriptions")
def write_prescription(req: PrescriptionWrite, bg: BackgroundTasks,
                       current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == current_user.get("doctor_id")).first()
    doctor_name = doctor.name if doctor else current_user.get("name", "Doctor")
    presc = Prescription(
        id=str(uuid.uuid4())[:50],
        appointment_id=req.appointment_id,
        patient_id=req.patient_id,
        doctor_id=current_user.get("doctor_id"),
        doctor_name=doctor_name,
        diagnosis=req.diagnosis,
        notes=req.notes,
        follow_up_date=req.follow_up_date,
        file_url=None,
        created_at=datetime.utcnow().isoformat(),
        hospital_id=current_user.get("hospital_id", "h1"),
    )
    db.add(presc)
    for m in req.medicines:
        db.add(PrescriptionMedicine(
            prescription_id=presc.id,
            name=m.name, dosage=m.dosage, frequency=m.frequency,
            duration=m.duration, instructions=m.instructions,
        ))
    db.commit()
    db.refresh(presc)
    bg.add_task(_notify_prescription, req.patient_id, doctor_name, req.diagnosis, req.follow_up_date)
    return presc.to_dict()


# ── Patients list with prescription history ────────────────────────────────────
@router.get("/patients")
def get_my_patients(current_user: dict = Depends(require_doctor), db: Session = Depends(get_db)):
    doctor_id = current_user.get("doctor_id")
    apts = db.query(Appointment).filter(Appointment.doctor_id == doctor_id).all()
    patient_ids = list({a.patient_id for a in apts})
    result = []
    for pid in patient_ids:
        patient = db.query(User).filter(User.id == pid).first()
        if not patient:
            continue
        pt_apts = [a for a in apts if a.patient_id == pid]
        prescs  = db.query(Prescription).filter(
            Prescription.doctor_id == doctor_id,
            Prescription.patient_id == pid,
        ).order_by(Prescription.created_at.desc()).all()
        result.append({
            "id":           pid,
            "name":         patient.name,
            "email":        patient.email,
            "phone":        patient.phone,
            "total_visits": len(pt_apts),
            "last_visit":   max((a.date for a in pt_apts), default=None),
            "prescriptions": [p.to_dict() for p in prescs],
        })
    return sorted(result, key=lambda p: p["last_visit"] or "", reverse=True)


# ── Background notification tasks ──────────────────────────────────────────────
def _notify_complete(patient_id: str, doctor_id: str):
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
        doctor_name = doctor.name if doctor else "your doctor"
        notif = Notification(
            id=str(uuid.uuid4())[:50],
            user_id=patient_id,
            type="appointment",
            title="Consultation Complete",
            message=f"Your consultation with {doctor_name} is complete. Prescription is ready.",
            read=False,
            action_url="/patient/prescriptions",
            created_at=datetime.utcnow().isoformat(),
        )
        db.add(notif)
        db.commit()
    finally:
        db.close()


def _notify_prescription(patient_id: str, doctor_name: str, diagnosis: str = "", follow_up: str = None):
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        msg = f"Dr. {doctor_name} has issued a prescription for you."
        if diagnosis:
            msg += f" Diagnosis: {diagnosis}."
        notif = Notification(
            id=str(uuid.uuid4())[:50],
            user_id=patient_id,
            type="prescription",
            title="New Prescription",
            message=msg,
            read=False,
            action_url="/patient/prescriptions",
            created_at=datetime.utcnow().isoformat(),
        )
        db.add(notif)
        db.commit()
        user = db.query(User).filter(User.id == patient_id).first()
        if user and user.phone:
            try:
                from app.whatsapp_service import wa_prescription_ready
                wa_prescription_ready(phone=user.phone, patient_name=user.name,
                                      doctor_name=doctor_name, diagnosis=diagnosis, follow_up=follow_up)
            except Exception:
                pass
    finally:
        db.close()


def _notify_followup_reminder(patient_id: str, doctor_name: str, follow_up_date: str):
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        try:
            fu = date.fromisoformat(follow_up_date)
            formatted = fu.strftime("%d %B %Y")
        except Exception:
            formatted = follow_up_date
        notif = Notification(
            id=str(uuid.uuid4())[:50],
            user_id=patient_id,
            type="follow_up",
            title="Follow-up Appointment Reminder",
            message=f"Dr. {doctor_name} has scheduled a follow-up for you on {formatted}.",
            read=False,
            action_url="/patient/appointments",
            created_at=datetime.utcnow().isoformat(),
        )
        db.add(notif)
        db.commit()
    finally:
        db.close()
