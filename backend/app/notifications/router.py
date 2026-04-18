from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.notifications.schemas import NotificationCreate, NotificationChannel
from app.mock_data import notifications_db, users_db, notification_log_db, next_id
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _get_phone(user_id: str) -> str | None:
    """Return the WhatsApp-ready phone number for a user, or None."""
    user = next((u for u in users_db if u["id"] == user_id), None)
    return user.get("phone") if user else None


def dispatch_notification(channel: str, user_id: str, message: str, **kwargs):
    """Log every dispatch; actually send WhatsApp when phone is available."""
    log_entry = {
        "id": next_id("notification"),
        "channel": channel,
        "user_id": user_id,
        "message": message,
        "status": "sent",
        "dispatched_at": datetime.utcnow().isoformat(),
        **kwargs,
    }
    notification_log_db.append(log_entry)

    if channel == "whatsapp":
        phone = kwargs.get("phone") or _get_phone(user_id)
        if phone:
            from app.whatsapp_service import _send_whatsapp
            _send_whatsapp(phone, message)
            log_entry["status"] = "whatsapp_sent"
        else:
            print(f"[WhatsApp] No phone for user {user_id} — skipped")
    elif channel == "email":
        print(f"[EMAIL] → {kwargs.get('email', 'unknown')}: {message}")
    elif channel == "sms":
        print(f"[SMS]   → {kwargs.get('phone', 'unknown')}: {message}")
    else:
        print(f"[PUSH]  → user {user_id}: {message}")

    return log_entry


# ── Reminder Helpers (called by background tasks) ─────────────────────────────

def send_appointment_reminder(patient_id: str, doctor_name: str,
                               time_slot: str, token: int = 0):
    user = next((u for u in users_db if u["id"] == patient_id), None)
    if not user:
        return
    patient_name = user.get("name", "Patient")
    phone = user.get("phone")

    msg_inapp = (f"Reminder: Your appointment with {doctor_name} is at "
                 f"{time_slot} today. Token #{token}. Please arrive 10 mins early.")
    notifications_db.append({
        "id": next_id("notification"),
        "user_id": patient_id,
        "type": "appointment_reminder",
        "title": "Appointment Reminder",
        "message": msg_inapp,
        "read": False,
        "action_url": "/patient/appointments",
        "created_at": datetime.utcnow().isoformat(),
    })

    if phone:
        from app.whatsapp_service import wa_appointment_reminder
        wa_appointment_reminder(phone, patient_name, doctor_name, time_slot, token)
    dispatch_notification("email", patient_id, msg_inapp, email=user.get("email", ""))


def send_medicine_reminder(patient_id: str, medicine_name: str,
                            dosage: str, time: str):
    user = next((u for u in users_db if u["id"] == patient_id), None)
    if not user:
        return
    patient_name = user.get("name", "Patient")
    phone = user.get("phone")
    msg = f"💊 Time to take {medicine_name} {dosage} at {time}."

    notifications_db.append({
        "id": next_id("notification"),
        "user_id": patient_id,
        "type": "medicine_reminder",
        "title": "Medicine Reminder",
        "message": msg,
        "read": False,
        "action_url": "/patient/medicine-reminders",
        "created_at": datetime.utcnow().isoformat(),
    })

    if phone:
        from app.whatsapp_service import wa_medicine_reminder
        wa_medicine_reminder(phone, patient_name, medicine_name, dosage, time)


def send_follow_up_reminder(patient_id: str, doctor_name: str, follow_up_date: str):
    msg = (f"Follow-up with {doctor_name} is due on {follow_up_date}. "
           f"Please book your appointment.")
    notifications_db.append({
        "id": next_id("notification"),
        "user_id": patient_id,
        "type": "follow_up_reminder",
        "title": "Follow-up Reminder",
        "message": msg,
        "read": False,
        "action_url": "/patient/book",
        "created_at": datetime.utcnow().isoformat(),
    })
    dispatch_notification("whatsapp", patient_id, msg)


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/")
def list_notifications(current_user: dict = Depends(get_current_user)):
    notifs = [n for n in notifications_db if n["user_id"] == current_user["id"]]
    return sorted(notifs, key=lambda x: x["created_at"], reverse=True)


@router.get("/unread-count")
def unread_count(current_user: dict = Depends(get_current_user)):
    count = sum(1 for n in notifications_db
                if n["user_id"] == current_user["id"] and not n["read"])
    return {"count": count}


@router.put("/{notif_id}/read")
def mark_read(notif_id: str, current_user: dict = Depends(get_current_user)):
    n = next((x for x in notifications_db
              if x["id"] == notif_id and x["user_id"] == current_user["id"]), None)
    if not n:
        raise HTTPException(404, "Notification not found")
    n["read"] = True
    return {"message": "Marked as read"}


@router.put("/read-all")
def mark_all_read(current_user: dict = Depends(get_current_user)):
    for n in notifications_db:
        if n["user_id"] == current_user["id"]:
            n["read"] = True
    return {"message": "All notifications marked as read"}


@router.post("/", dependencies=[Depends(require_admin)])
def create_notification(req: NotificationCreate):
    n = {
        "id": next_id("notification"),
        "user_id": req.user_id,
        "type": req.type,
        "title": req.title,
        "message": req.message,
        "read": False,
        "action_url": req.action_url,
        "created_at": datetime.utcnow().isoformat(),
    }
    notifications_db.append(n)
    return n


@router.post("/broadcast", dependencies=[Depends(require_admin)])
def broadcast(req: NotificationCreate, background_tasks: BackgroundTasks):
    patients = [u for u in users_db if u["role"] == "patient"]
    created = []
    for p in patients:
        n = {
            "id": next_id("notification"),
            "user_id": p["id"],
            "type": req.type,
            "title": req.title,
            "message": req.message,
            "read": False,
            "action_url": req.action_url,
            "created_at": datetime.utcnow().isoformat(),
        }
        notifications_db.append(n)
        created.append(n)
        background_tasks.add_task(
            dispatch_notification, "whatsapp", p["id"], req.message
        )
    return {"sent": len(created), "notifications": created}


@router.get("/dispatch-log", dependencies=[Depends(require_admin)])
def get_dispatch_log():
    return notification_log_db[-50:]


@router.post("/test-whatsapp")
def test_whatsapp(current_user: dict = Depends(get_current_user)):
    """Send a test WhatsApp message to the logged-in user's phone."""
    phone = _get_phone(current_user["id"])
    if not phone:
        raise HTTPException(400, "No phone number set for your account")
    from app.whatsapp_service import _send_whatsapp, HOSPITAL_NAME
    ok = _send_whatsapp(phone, f"✅ Test message from {HOSPITAL_NAME}. WhatsApp notifications are working!")
    return {"sent": ok, "phone": phone}
