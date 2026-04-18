from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.medicine_reminders.schemas import MedicineReminderCreate, MedicineReminderUpdate
from app.mock_data import medicine_reminders_db, next_id
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/medicine-reminders", tags=["Medicine Reminders"])

@router.get("/")
def list_reminders(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "admin":
        return medicine_reminders_db
    return [r for r in medicine_reminders_db if r["patient_id"] == current_user["id"]]

@router.get("/active")
def active_reminders(current_user: dict = Depends(get_current_user)):
    today = datetime.utcnow().date().isoformat()
    reminders = [r for r in medicine_reminders_db
                 if r["patient_id"] == current_user["id"]
                 and r["active"]
                 and r["start_date"] <= today
                 and (not r["end_date"] or r["end_date"] >= today)]
    return reminders

@router.post("/")
def create_reminder(req: MedicineReminderCreate, current_user: dict = Depends(get_current_user)):
    reminder = {
        "id": next_id("medicine_reminder"),
        "patient_id": current_user["id"],
        "medicine_name": req.medicine_name,
        "dosage": req.dosage,
        "frequency": req.frequency,
        "times": req.times,
        "start_date": req.start_date,
        "end_date": req.end_date,
        "instructions": req.instructions or "",
        "active": True,
        "prescription_id": req.prescription_id,
        "created_at": datetime.utcnow().isoformat(),
    }
    medicine_reminders_db.append(reminder)
    return reminder

@router.put("/{reminder_id}")
def update_reminder(reminder_id: str, req: MedicineReminderUpdate, current_user: dict = Depends(get_current_user)):
    r = next((x for x in medicine_reminders_db if x["id"] == reminder_id and x["patient_id"] == current_user["id"]), None)
    if not r:
        raise HTTPException(404, "Reminder not found")
    r.update(req.model_dump(exclude_none=True))
    return r

@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: str, current_user: dict = Depends(get_current_user)):
    r = next((x for x in medicine_reminders_db if x["id"] == reminder_id and x["patient_id"] == current_user["id"]), None)
    if not r:
        raise HTTPException(404, "Reminder not found")
    medicine_reminders_db[:] = [x for x in medicine_reminders_db if x["id"] != reminder_id]
    return {"message": "Reminder deleted"}

@router.post("/{reminder_id}/trigger", dependencies=[Depends(require_admin)])
def trigger_reminder(reminder_id: str, background_tasks: BackgroundTasks):
    """Admin: manually trigger a medicine reminder notification (simulates scheduler)"""
    from app.notifications.router import send_medicine_reminder
    r = next((x for x in medicine_reminders_db if x["id"] == reminder_id), None)
    if not r:
        raise HTTPException(404, "Reminder not found")
    time_str = r["times"][0] if r["times"] else "now"
    background_tasks.add_task(send_medicine_reminder, r["patient_id"], r["medicine_name"], r["dosage"], time_str)
    return {"message": f"Reminder triggered for {r['medicine_name']}"}
