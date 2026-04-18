from fastapi import APIRouter, HTTPException, Depends
from datetime import date
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Appointment, Doctor, Specialization, QueueState, QueueHistory
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/queue", tags=["Queue"])


def _enrich(apt: Appointment, db: Session) -> dict:
    d = apt.to_dict()
    doctor = db.query(Doctor).filter(Doctor.id == apt.doctor_id).first()
    spec   = db.query(Specialization).filter(Specialization.id == apt.specialization_id).first()
    d["doctor"]        = doctor.to_dict() if doctor else None
    d["specialization"] = spec.to_dict() if spec else None
    return d


def _avg_consult_minutes(doctor_id: str, db: Session) -> int:
    history = db.query(QueueHistory).filter(
        QueueHistory.doctor_id == doctor_id,
        QueueHistory.patients_ahead > 0,
    ).all()
    if not history:
        return 15
    per_patient = [h.actual_wait_minutes / h.patients_ahead for h in history]
    return max(5, round(sum(per_patient) / len(per_patient)))


def _patients_ahead_count(apt_dict: dict, all_waiting: list) -> int:
    if apt_dict["status"] != "waiting":
        return 0
    is_priority = apt_dict.get("priority", False)
    ahead = 0
    for w in all_waiting:
        if w["id"] == apt_dict["id"]:
            continue
        w_prio = w.get("priority", False)
        if is_priority:
            if w_prio and w["token_number"] < apt_dict["token_number"]:
                ahead += 1
        else:
            if w_prio or w["token_number"] < apt_dict["token_number"]:
                ahead += 1
    return ahead


def _today() -> str:
    return date.today().isoformat()


@router.get("/{doctor_id}")
def get_queue(doctor_id: str, date_str: str = None,
              current_user: dict = Depends(get_current_user),
              db: Session = Depends(get_db)):
    d = date_str or _today()
    state = db.query(QueueState).filter(QueueState.id == f"{doctor_id}:{d}").first()
    current = state.current_token if state else 0

    apts = sorted(
        db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == d,
            Appointment.status != "cancelled",
        ).all(),
        key=lambda x: x.token_number,
    )

    avg_min = _avg_consult_minutes(doctor_id, db)
    waiting = [a.to_dict() for a in apts if a.status == "waiting"]
    in_progress = next((a for a in apts if a.status == "in_progress"), None)

    enriched = []
    for a in apts:
        e = _enrich(a, db)
        ahead = _patients_ahead_count(e, waiting)
        e["patients_ahead"] = ahead
        in_prog_buffer = (avg_min // 2) if in_progress and a.status == "waiting" else 0
        e["estimated_wait_minutes"] = (ahead * avg_min + in_prog_buffer) if a.status == "waiting" else 0
        e["avg_consult_minutes"] = avg_min
        enriched.append(e)

    return {
        "doctor_id": doctor_id, "date": d, "current_token": current,
        "total_patients": len(apts), "avg_consult_minutes": avg_min,
        "appointments": enriched,
    }


@router.get("/{doctor_id}/my-status")
def my_status(doctor_id: str, date_str: str = None,
              current_user: dict = Depends(get_current_user),
              db: Session = Depends(get_db)):
    d     = date_str or _today()
    state = db.query(QueueState).filter(QueueState.id == f"{doctor_id}:{d}").first()
    current = state.current_token if state else 0

    apt = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == d,
        Appointment.patient_id == current_user["id"],
        Appointment.status != "cancelled",
    ).first()
    if not apt:
        raise HTTPException(404, "No appointment found for today with this doctor")

    avg_min = _avg_consult_minutes(doctor_id, db)
    waiting = [a.to_dict() for a in db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == d,
        Appointment.status == "waiting",
    ).all()]
    in_progress = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == d,
        Appointment.status == "in_progress",
    ).first()

    apt_dict = apt.to_dict()
    ahead = _patients_ahead_count(apt_dict, waiting) if apt.status == "waiting" else 0
    in_prog_buffer = (avg_min // 2) if in_progress and apt.status == "waiting" else 0
    estimated = (ahead * avg_min + in_prog_buffer) if apt.status == "waiting" else 0

    return {
        "my_token":               apt.token_number,
        "current_token":          current,
        "patients_ahead":         ahead,
        "estimated_wait_minutes": estimated,
        "avg_consult_minutes":    avg_min,
        "status":                 apt.status,
        "appointment":            _enrich(apt, db),
    }


@router.post("/{doctor_id}/next", dependencies=[Depends(require_admin)])
def next_patient(doctor_id: str, date_str: str = None, db: Session = Depends(get_db)):
    d   = date_str or _today()
    key = f"{doctor_id}:{d}"

    state = db.query(QueueState).filter(QueueState.id == key).first()
    if not state:
        state = QueueState(id=key, doctor_id=doctor_id, date=d, current_token=0)
        db.add(state)

    cur = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == d,
        Appointment.status == "in_progress",
    ).first()
    if cur:
        cur.status = "completed"

    state.current_token += 1
    new_token = state.current_token

    nxt = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == d,
        Appointment.token_number == new_token,
        Appointment.status == "waiting",
    ).first()
    if nxt:
        nxt.status = "in_progress"

    db.commit()
    return {"current_token": new_token, "message": f"Now serving token #{new_token}"}


@router.post("/{doctor_id}/skip/{appointment_id}", dependencies=[Depends(require_admin)])
def skip_patient(doctor_id: str, appointment_id: str, date_str: str = None, db: Session = Depends(get_db)):
    d   = date_str or _today()
    apt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    apt.status = "skipped"

    key = f"{doctor_id}:{d}"
    state = db.query(QueueState).filter(QueueState.id == key).first()
    if not state:
        state = QueueState(id=key, doctor_id=doctor_id, date=d, current_token=0)
        db.add(state)
    state.current_token += 1
    new_token = state.current_token

    nxt = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == d,
        Appointment.token_number == new_token,
        Appointment.status == "waiting",
    ).first()
    if nxt:
        nxt.status = "in_progress"

    db.commit()
    return {"message": f"Patient skipped. Now serving token #{new_token}"}


@router.post("/{doctor_id}/complete/{appointment_id}", dependencies=[Depends(require_admin)])
def complete_appointment_queue(doctor_id: str, appointment_id: str, db: Session = Depends(get_db)):
    apt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not apt:
        raise HTTPException(404, "Appointment not found")
    apt.status = "completed"
    db.commit()
    return {"message": "Appointment marked as completed"}
