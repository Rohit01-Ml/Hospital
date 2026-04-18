"""DB-safe notification helpers for use in background tasks."""
import uuid
from datetime import datetime


def _new_id() -> str:
    return str(uuid.uuid4())[:20]


def create_notification(user_id: str, ntype: str, title: str,
                         message: str, action_url: str = "") -> None:
    """Insert a notification row. Creates its own DB session (safe for bg tasks)."""
    from app.database import SessionLocal
    from app.models import Notification
    db = SessionLocal()
    try:
        n = Notification(
            id=_new_id(),
            user_id=user_id,
            type=ntype,
            title=title,
            message=message,
            read=False,
            action_url=action_url,
            created_at=datetime.utcnow().isoformat(),
        )
        db.add(n)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[notify] error: {e}")
    finally:
        db.close()


def send_appointment_reminder(patient_id: str, doctor_name: str,
                               time_slot: str, token: int = 0) -> None:
    from app.database import SessionLocal
    from app.models import User, Notification
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == patient_id).first()
        if not user:
            return
        msg = (f"Reminder: Your appointment with {doctor_name} is at "
               f"{time_slot} today. Token #{token}. Please arrive 10 mins early.")
        n = Notification(
            id=_new_id(), user_id=patient_id,
            type="appointment_reminder", title="Appointment Reminder",
            message=msg, read=False,
            action_url="/patient/appointments",
            created_at=datetime.utcnow().isoformat(),
        )
        db.add(n)
        db.commit()
        if user.phone:
            from app.whatsapp_service import wa_appointment_reminder
            wa_appointment_reminder(user.phone, user.name, doctor_name, time_slot, token)
    except Exception as e:
        db.rollback()
        print(f"[notify] appointment reminder error: {e}")
    finally:
        db.close()


def send_medicine_reminder(patient_id: str, medicine_name: str,
                            dosage: str, time: str) -> None:
    from app.database import SessionLocal
    from app.models import User, Notification
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == patient_id).first()
        if not user:
            return
        msg = f"Time to take {medicine_name} {dosage} at {time}."
        n = Notification(
            id=_new_id(), user_id=patient_id,
            type="medicine_reminder", title="Medicine Reminder",
            message=msg, read=False,
            action_url="/patient/medicine-reminders",
            created_at=datetime.utcnow().isoformat(),
        )
        db.add(n)
        db.commit()
        if user.phone:
            from app.whatsapp_service import wa_medicine_reminder
            wa_medicine_reminder(user.phone, user.name, medicine_name, dosage, time)
    except Exception as e:
        db.rollback()
        print(f"[notify] medicine reminder error: {e}")
    finally:
        db.close()
