import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.prescriptions.schemas import PrescriptionCreate, PrescriptionUpdate
from app.database import get_db
from app.models import Prescription, PrescriptionMedicine, Appointment, Doctor, User
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


def _enrich(p: Prescription, db: Session) -> dict:
    d = p.to_dict()
    doc = db.query(Doctor).filter(Doctor.id == p.doctor_id).first()
    apt = db.query(Appointment).filter(Appointment.id == p.appointment_id).first() if p.appointment_id else None
    pat = db.query(User).filter(User.id == p.patient_id).first()
    d["doctor"] = doc.to_dict() if doc else None
    d["appointment"] = apt.to_dict() if apt else None
    d["patient_name"] = pat.name if pat else "Unknown"
    return d


def _notify_prescription(patient_id: str, doctor_name: str):
    from app.notify import create_notification
    create_notification(
        patient_id, "prescription_ready", "Prescription Available",
        f"{doctor_name} has uploaded your prescription. View and manage your medicines.",
        "/patient/prescriptions",
    )


@router.get("/")
def list_prescriptions(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Prescription)
    if current_user["role"] != "admin":
        q = q.filter(Prescription.patient_id == current_user["id"])
    return [_enrich(p, db) for p in q.all()]


@router.get("/{presc_id}")
def get_prescription(presc_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(Prescription).filter(Prescription.id == presc_id).first()
    if not p:
        raise HTTPException(404, "Prescription not found")
    if current_user["role"] != "admin" and p.patient_id != current_user["id"]:
        raise HTTPException(403, "Not authorized")
    return _enrich(p, db)


@router.post("/", dependencies=[Depends(require_admin)])
def create_prescription(req: PrescriptionCreate, background_tasks: BackgroundTasks,
                        current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == req.appointment_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    doc = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first()
    doctor_name = doc.name if doc else "Doctor"

    presc = Prescription(
        id=str(uuid.uuid4())[:20],
        appointment_id=req.appointment_id,
        patient_id=req.patient_id,
        doctor_id=apt.doctor_id,
        doctor_name=doctor_name,
        diagnosis=req.diagnosis,
        notes=req.notes or "",
        follow_up_date=req.follow_up_date,
        file_url=None,
        created_at=datetime.utcnow().isoformat(),
    )
    db.add(presc)
    db.flush()
    for m in req.medicines:
        db.add(PrescriptionMedicine(prescription_id=presc.id, **m.model_dump()))
    db.commit()
    db.refresh(presc)
    background_tasks.add_task(_notify_prescription, req.patient_id, doctor_name)
    return _enrich(presc, db)


@router.put("/{presc_id}", dependencies=[Depends(require_admin)])
def update_prescription(presc_id: str, req: PrescriptionUpdate, db: Session = Depends(get_db)):
    p = db.query(Prescription).filter(Prescription.id == presc_id).first()
    if not p:
        raise HTTPException(404, "Prescription not found")
    updates = req.model_dump(exclude_none=True)
    if "medicines" in updates:
        # Replace medicines
        db.query(PrescriptionMedicine).filter(PrescriptionMedicine.prescription_id == presc_id).delete()
        for m in req.medicines:
            md = m.model_dump() if hasattr(m, "model_dump") else m
            db.add(PrescriptionMedicine(prescription_id=presc_id, **md))
        updates.pop("medicines")
    for k, v in updates.items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return _enrich(p, db)


@router.get("/{presc_id}/download")
def download_prescription(presc_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    p = db.query(Prescription).filter(Prescription.id == presc_id).first()
    if not p:
        raise HTTPException(404, "Prescription not found")
    if current_user["role"] != "admin" and p.patient_id != current_user["id"]:
        raise HTTPException(403, "Not authorized")
    return {
        "download_url": f"mock://prescriptions/{presc_id}.pdf",
        "filename": f"prescription_{presc_id}.pdf",
        "prescription": _enrich(p, db),
    }
