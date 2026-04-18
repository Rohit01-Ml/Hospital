import uuid
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from app.doctors.schemas import DoctorCreate, DoctorUpdate, AvailabilityCreate, AvailabilityUpdate
from app.database import get_db
from app.models import Doctor, Specialization, Availability, Appointment
from app.dependencies import require_admin, get_current_user

router = APIRouter(prefix="/doctors", tags=["Doctors"])


def _enrich_doc(doc: Doctor, db: Session) -> dict:
    d = doc.to_dict()
    spec = db.query(Specialization).filter(Specialization.id == doc.specialization_id).first()
    d["specialization"] = spec.to_dict() if spec else None
    return d


@router.get("/")
def list_doctors(specialization_id: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Doctor)
    if specialization_id:
        q = q.filter(Doctor.specialization_id == specialization_id)
    return [_enrich_doc(d, db) for d in q.all()]


@router.get("/{doctor_id}")
def get_doctor(doctor_id: str, db: Session = Depends(get_db)):
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(404, "Doctor not found")
    return _enrich_doc(doc, db)


@router.post("/", dependencies=[Depends(require_admin)])
def create_doctor(req: DoctorCreate, db: Session = Depends(get_db)):
    spec = db.query(Specialization).filter(Specialization.id == req.specialization_id).first()
    if not spec:
        raise HTTPException(404, "Specialization not found")
    doc = Doctor(
        id=str(uuid.uuid4())[:10],
        rating=4.5, patients_treated=0, image_url=None,
        **req.model_dump(),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return _enrich_doc(doc, db)


@router.put("/{doctor_id}", dependencies=[Depends(require_admin)])
def update_doctor(doctor_id: str, req: DoctorUpdate, db: Session = Depends(get_db)):
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(404, "Doctor not found")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(doc, k, v)
    db.commit()
    db.refresh(doc)
    return _enrich_doc(doc, db)


@router.delete("/{doctor_id}", dependencies=[Depends(require_admin)])
def delete_doctor(doctor_id: str, db: Session = Depends(get_db)):
    doc = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doc:
        raise HTTPException(404, "Doctor not found")
    db.delete(doc)
    db.commit()
    return {"message": "Doctor deleted"}


# ── Availability ───────────────────────────────────────────────────────────────

@router.get("/{doctor_id}/availability")
def get_availability(doctor_id: str, db: Session = Depends(get_db)):
    return [a.to_dict() for a in
            db.query(Availability).filter(Availability.doctor_id == doctor_id).all()]


@router.post("/availability", dependencies=[Depends(require_admin)])
def create_availability(req: AvailabilityCreate, db: Session = Depends(get_db)):
    av = Availability(id=str(uuid.uuid4())[:10], **req.model_dump())
    db.add(av)
    db.commit()
    db.refresh(av)
    return av.to_dict()


@router.put("/availability/{av_id}", dependencies=[Depends(require_admin)])
def update_availability(av_id: str, req: AvailabilityUpdate, db: Session = Depends(get_db)):
    av = db.query(Availability).filter(Availability.id == av_id).first()
    if not av:
        raise HTTPException(404, "Availability not found")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(av, k, v)
    db.commit()
    db.refresh(av)
    return av.to_dict()


@router.delete("/availability/{av_id}", dependencies=[Depends(require_admin)])
def delete_availability(av_id: str, db: Session = Depends(get_db)):
    av = db.query(Availability).filter(Availability.id == av_id).first()
    if not av:
        raise HTTPException(404, "Availability not found")
    db.delete(av)
    db.commit()
    return {"message": "Deleted"}


# ── Slots ──────────────────────────────────────────────────────────────────────

@router.get("/{doctor_id}/slots")
def get_slots(doctor_id: str, date_str: str, db: Session = Depends(get_db)):
    try:
        target = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD")

    dow = target.weekday()
    avails = db.query(Availability).filter(
        Availability.doctor_id == doctor_id,
        Availability.day_of_week == dow,
    ).all()
    if not avails:
        return []

    booked = {
        a.time_slot for a in
        db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == date_str,
            Appointment.status != "cancelled",
        ).all()
    }

    slots = []
    for av in avails:
        cur = datetime.strptime(av.start_time, "%H:%M")
        end = datetime.strptime(av.end_time, "%H:%M")
        while cur < end:
            t = cur.strftime("%H:%M")
            slots.append({"time": t, "available": t not in booked, "availability_id": av.id})
            cur += timedelta(minutes=av.slot_duration_minutes)
    return slots
