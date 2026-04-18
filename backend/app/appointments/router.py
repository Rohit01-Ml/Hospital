import uuid
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.appointments.schemas import AppointmentCreate, AppointmentUpdate
from app.database import get_db
from app.models import Appointment, Doctor, Specialization, User, Payment, QueueState
from app.dependencies import get_current_user, require_admin
from app.payments.router import CONSULTATION_FEES

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def _enrich(apt: Appointment, db: Session) -> dict:
    d = apt.to_dict()
    doctor = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first()
    spec   = db.query(Specialization).filter(Specialization.id == apt.specialization_id).first()
    d["doctor"]        = doctor.to_dict() if doctor else None
    d["specialization"] = spec.to_dict() if spec else None
    return d


def _wa_booking_notify(patient_id: str, doctor_id: str, apt_date: str,
                       time_slot: str, token: int, spec_id: str):
    from app.database import SessionLocal
    from app.models import User as UserM, Doctor as DocM
    db2 = SessionLocal()
    try:
        user   = db2.query(UserM).filter(UserM.id == patient_id).first()
        doctor = db2.query(DocM).filter(DocM.id == doctor_id).first()
        if not user or not user.phone:
            return
        fee = CONSULTATION_FEES.get(spec_id, 300)
        from app.whatsapp_service import wa_appointment_booked
        wa_appointment_booked(
            phone=user.phone,
            patient_name=user.name,
            doctor_name=doctor.name if doctor else "Doctor",
            date=apt_date,
            time_slot=time_slot,
            token=token,
            fee=fee,
        )
    finally:
        db2.close()


@router.get("/")
def list_appointments(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Appointment)
    if current_user["role"] != "admin":
        q = q.filter(Appointment.patient_id == current_user["id"])
    return [_enrich(a, db) for a in q.all()]


@router.get("/today")
def today_appointments(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today().isoformat()
    q = db.query(Appointment).filter(Appointment.date == today)
    if current_user["role"] != "admin":
        q = q.filter(Appointment.patient_id == current_user["id"])
    return [_enrich(a, db) for a in q.all()]


@router.get("/{apt_id}")
def get_appointment(apt_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if current_user["role"] != "admin" and apt.patient_id != current_user["id"]:
        raise HTTPException(403, "Not authorized")
    return _enrich(apt, db)


@router.post("/")
def book_appointment(req: AppointmentCreate, bg: BackgroundTasks,
                     current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    staff_roles = ("admin", "doctor", "receptionist")
    booking_patient_id = req.patient_id if (current_user["role"] in staff_roles and req.patient_id) else current_user["id"]

    conflict = db.query(Appointment).filter(
        Appointment.doctor_id == req.doctor_id,
        Appointment.date == req.date,
        Appointment.time_slot == req.time_slot,
        Appointment.status != "cancelled",
    ).first()
    if conflict:
        raise HTTPException(400, "This time slot is already booked")

    token_number = db.query(Appointment).filter(
        Appointment.doctor_id == req.doctor_id,
        Appointment.date == req.date,
        Appointment.status != "cancelled",
    ).count() + 1

    apt = Appointment(
        id=str(uuid.uuid4())[:20],
        patient_id=booking_patient_id,
        doctor_id=req.doctor_id,
        specialization_id=req.specialization_id,
        date=req.date,
        time_slot=req.time_slot,
        token_number=token_number,
        status="waiting",
        notes=req.notes or "",
        priority=False,
        booked_by=current_user["id"],
        booked_by_role=current_user["role"],
    )
    db.add(apt)

    key = f"{req.doctor_id}:{req.date}"
    if not db.query(QueueState).filter(QueueState.id == key).first():
        db.add(QueueState(id=key, doctor_id=req.doctor_id, date=req.date, current_token=0))

    if current_user["role"] in staff_roles and req.payment_method in ("cash", "upi"):
        fee = CONSULTATION_FEES.get(req.specialization_id, 300)
        db.add(Payment(
            id=str(uuid.uuid4())[:20],
            appointment_id=apt.id,
            patient_id=booking_patient_id,
            amount=fee,
            currency="INR",
            status="paid",
            razorpay_order_id=f"walkin_{apt.id}",
            razorpay_payment_id=f"{req.payment_method}_{apt.id}",
            method=req.payment_method,
            created_at=datetime.utcnow().isoformat(),
        ))

    db.commit()
    db.refresh(apt)
    bg.add_task(_wa_booking_notify, booking_patient_id, req.doctor_id,
                req.date, req.time_slot, token_number, req.specialization_id)
    return _enrich(apt, db)


@router.put("/{apt_id}")
def update_appointment(apt_id: str, req: AppointmentUpdate,
                       current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if current_user["role"] != "admin":
        if apt.patient_id != current_user["id"]:
            raise HTTPException(403, "Not authorized")
        if req.status and req.status != "cancelled":
            raise HTTPException(403, "Patients can only cancel appointments")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(apt, k, v)
    db.commit()
    db.refresh(apt)
    return _enrich(apt, db)


@router.delete("/{apt_id}")
def cancel_appointment(apt_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == apt_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    if current_user["role"] != "admin" and apt.patient_id != current_user["id"]:
        raise HTTPException(403, "Not authorized")
    apt.status = "cancelled"
    db.commit()
    return {"message": "Appointment cancelled"}
