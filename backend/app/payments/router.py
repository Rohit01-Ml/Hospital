import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.payments.schemas import PaymentInitiate, PaymentVerify
from app.database import get_db
from app.models import Payment, Appointment, User, Doctor
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/payments", tags=["Payments"])

CONSULTATION_FEES = {"s1": 500, "s2": 800, "s3": 700, "s4": 600, "s5": 400, "s6": 300}


def _notify_payment(patient_id: str, amount: float, apt_id: str):
    from app.notify import create_notification
    from app.database import SessionLocal
    db2 = SessionLocal()
    try:
        user = db2.query(User).filter(User.id == patient_id).first()
        apt  = db2.query(Appointment).filter(Appointment.id == apt_id).first()
        doctor = db2.query(Doctor).filter(Doctor.id == apt.doctor_id).first() if apt else None
        create_notification(
            patient_id, "payment_success", "Payment Confirmed ✓",
            f"Payment of ₹{amount:.0f} confirmed. Appointment #{apt_id} is booked.",
            "/patient/appointments",
        )
        if user and user.phone and apt and doctor:
            from app.whatsapp_service import wa_payment_success
            wa_payment_success(
                phone=user.phone,
                patient_name=user.name,
                amount=amount,
                doctor_name=doctor.name,
                date=apt.date,
            )
    except Exception as e:
        print(f"[payments] notify error: {e}")
    finally:
        db2.close()


@router.get("/")
def list_payments(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Payment)
    if current_user["role"] != "admin":
        q = q.filter(Payment.patient_id == current_user["id"])
    return [p.to_dict() for p in q.all()]


@router.get("/appointment/{apt_id}")
def get_payment_by_appointment(apt_id: str, current_user: dict = Depends(get_current_user),
                                db: Session = Depends(get_db)):
    pay = db.query(Payment).filter(Payment.appointment_id == apt_id).first()
    if not pay:
        raise HTTPException(404, "Payment not found for this appointment")
    return pay.to_dict()


@router.post("/initiate")
def initiate_payment(req: PaymentInitiate, current_user: dict = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == req.appointment_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")

    existing = db.query(Payment).filter(
        Payment.appointment_id == req.appointment_id,
        Payment.status == "paid",
    ).first()
    if existing:
        raise HTTPException(400, "Payment already completed for this appointment")

    fee = CONSULTATION_FEES.get(apt.specialization_id, req.amount or 300)
    order_id = f"order_{uuid.uuid4().hex[:12]}"

    payment = Payment(
        id=str(uuid.uuid4())[:20],
        appointment_id=req.appointment_id,
        patient_id=current_user["id"],
        amount=fee,
        currency=req.currency,
        status="pending",
        razorpay_order_id=order_id,
        razorpay_payment_id=None,
        method=None,
        created_at=datetime.utcnow().isoformat(),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    d = payment.to_dict()
    d["razorpay_key"] = "rzp_test_MOCK_KEY_FOR_DEMO"
    d["name"] = "MediCare+ Hospital"
    d["description"] = f"Consultation Fee - Appointment #{req.appointment_id}"
    return d


@router.post("/verify")
def verify_payment(req: PaymentVerify, background_tasks: BackgroundTasks,
                   current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    pay = db.query(Payment).filter(Payment.razorpay_order_id == req.razorpay_order_id).first()
    if not pay:
        raise HTTPException(404, "Order not found")
    pay.status = "paid"
    pay.razorpay_payment_id = req.razorpay_payment_id
    pay.method = "mock_verified"
    db.commit()
    db.refresh(pay)
    background_tasks.add_task(_notify_payment, pay.patient_id, pay.amount, pay.appointment_id)
    return {"success": True, "payment": pay.to_dict()}


@router.post("/mock-pay/{appointment_id}")
def mock_instant_pay(appointment_id: str, background_tasks: BackgroundTasks,
                     current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")

    existing = db.query(Payment).filter(Payment.appointment_id == appointment_id).first()
    fee = CONSULTATION_FEES.get(apt.specialization_id, 300)

    if existing:
        existing.status = "paid"
        existing.razorpay_payment_id = f"pay_{uuid.uuid4().hex[:10]}"
        existing.method = "mock"
        db.commit()
        db.refresh(existing)
        pay = existing
    else:
        pay = Payment(
            id=str(uuid.uuid4())[:20],
            appointment_id=appointment_id,
            patient_id=current_user["id"],
            amount=fee,
            currency="INR",
            status="paid",
            razorpay_order_id=f"order_{uuid.uuid4().hex[:12]}",
            razorpay_payment_id=f"pay_{uuid.uuid4().hex[:10]}",
            method="mock",
            created_at=datetime.utcnow().isoformat(),
        )
        db.add(pay)
        db.commit()
        db.refresh(pay)

    background_tasks.add_task(_notify_payment, pay.patient_id, pay.amount, appointment_id)
    return {"success": True, "payment": pay.to_dict()}
