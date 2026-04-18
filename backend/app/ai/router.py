"""AI-powered features: Symptom Checker, Smart Queue, Smart Slot Recommendation."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.mock_data import (
    specializations_db, doctors_db, availability_db,
    appointments_db, queue_state_db, queue_history_db,
)
from datetime import datetime, date, timedelta

router = APIRouter(prefix="/ai", tags=["AI Features"])

# ── Symptom → Specialization keyword map ──────────────────────────────────────
_SYMPTOM_MAP: dict[str, list[tuple[str, float]]] = {
    "chest pain":          [("Cardiology", 0.90), ("General Medicine", 0.55)],
    "heart":               [("Cardiology", 0.88)],
    "palpitation":         [("Cardiology", 0.82)],
    "palpitations":        [("Cardiology", 0.82)],
    "shortness of breath": [("Cardiology", 0.72), ("General Medicine", 0.45)],
    "breathless":          [("Cardiology", 0.68)],
    "hypertension":        [("Cardiology", 0.85), ("General Medicine", 0.60)],
    "blood pressure":      [("Cardiology", 0.82), ("General Medicine", 0.55)],
    "angina":              [("Cardiology", 0.92)],
    "headache":            [("Neurology", 0.72), ("General Medicine", 0.50)],
    "migraine":            [("Neurology", 0.90)],
    "seizure":             [("Neurology", 0.95)],
    "stroke":              [("Neurology", 0.95)],
    "memory loss":         [("Neurology", 0.85)],
    "dizziness":           [("Neurology", 0.65), ("General Medicine", 0.50)],
    "numbness":            [("Neurology", 0.75)],
    "tremor":              [("Neurology", 0.85)],
    "joint pain":          [("Orthopedics", 0.88)],
    "knee pain":           [("Orthopedics", 0.92)],
    "back pain":           [("Orthopedics", 0.80), ("General Medicine", 0.40)],
    "fracture":            [("Orthopedics", 0.97)],
    "sprain":              [("Orthopedics", 0.85)],
    "spine":               [("Orthopedics", 0.88)],
    "arthritis":           [("Orthopedics", 0.88)],
    "shoulder pain":       [("Orthopedics", 0.82)],
    "bone":                [("Orthopedics", 0.80)],
    "skin rash":           [("Dermatology", 0.92)],
    "rash":                [("Dermatology", 0.88)],
    "acne":                [("Dermatology", 0.90)],
    "hair loss":           [("Dermatology", 0.85)],
    "itching":             [("Dermatology", 0.78)],
    "eczema":              [("Dermatology", 0.92)],
    "psoriasis":           [("Dermatology", 0.95)],
    "skin":                [("Dermatology", 0.75)],
    "child":               [("Pediatrics", 0.88)],
    "infant":              [("Pediatrics", 0.95)],
    "baby":                [("Pediatrics", 0.95)],
    "vaccination":         [("Pediatrics", 0.88)],
    "fever":               [("General Medicine", 0.82), ("Pediatrics", 0.35)],
    "cold":                [("General Medicine", 0.72)],
    "cough":               [("General Medicine", 0.68)],
    "flu":                 [("General Medicine", 0.78)],
    "fatigue":             [("General Medicine", 0.65)],
    "weakness":            [("General Medicine", 0.62)],
    "stomach":             [("General Medicine", 0.65)],
    "nausea":              [("General Medicine", 0.68)],
    "vomiting":            [("General Medicine", 0.70)],
    "diarrhea":            [("General Medicine", 0.72)],
    "diabetes":            [("General Medicine", 0.75)],
    "pain":                [("General Medicine", 0.50)],
}

_REASONS = {
    "Cardiology":       "Your symptoms suggest a cardiac evaluation is advisable.",
    "Neurology":        "Neurological assessment recommended based on your symptoms.",
    "Orthopedics":      "Musculoskeletal issue detected — orthopedic evaluation advised.",
    "Dermatology":      "Skin-related symptoms identified — dermatologist consultation recommended.",
    "Pediatrics":       "Child-specific symptoms noted — pediatric evaluation recommended.",
    "General Medicine": "A general physician can perform an initial evaluation.",
}


def _check_symptoms(text: str) -> list[dict]:
    lower = text.lower()
    scores: dict[str, float] = {}
    matched: dict[str, list[str]] = {}

    for keyword, spec_list in _SYMPTOM_MAP.items():
        if keyword in lower:
            for spec_name, confidence in spec_list:
                if confidence > scores.get(spec_name, 0.0):
                    scores[spec_name] = confidence
                matched.setdefault(spec_name, [])
                if keyword not in matched[spec_name]:
                    matched[spec_name].append(keyword)

    if not scores:
        return [{"specialization": "General Medicine", "specialization_id": "s6",
                 "icon": "local_hospital", "confidence": 0.50, "confidence_pct": "50%",
                 "available_doctors": len([d for d in doctors_db if d["specialization_id"] == "s6" and d["available"]]),
                 "reason": "No specific symptoms matched — a general physician can evaluate further.",
                 "matched_keywords": []}]

    results = []
    for spec_name, conf in sorted(scores.items(), key=lambda x: -x[1])[:3]:
        spec = next((s for s in specializations_db if s["name"] == spec_name), None)
        if spec:
            docs = [d for d in doctors_db if d["specialization_id"] == spec["id"] and d["available"]]
            results.append({
                "specialization": spec_name,
                "specialization_id": spec["id"],
                "icon": spec.get("icon", "medical_services"),
                "confidence": round(conf, 2),
                "confidence_pct": f"{int(conf * 100)}%",
                "available_doctors": len(docs),
                "reason": _REASONS.get(spec_name, "Specialist evaluation recommended."),
                "matched_keywords": matched.get(spec_name, []),
            })
    return results


def _predict_wait(doctor_id: str, patients_ahead: int) -> dict:
    history = [h for h in queue_history_db if h["doctor_id"] == doctor_id]
    if not history:
        avail = next((a for a in availability_db if a["doctor_id"] == doctor_id), None)
        duration = avail["slot_duration_minutes"] if avail else 20
        return {"predicted_minutes": patients_ahead * duration, "confidence": "low",
                "data_points": 0, "method": "slot_duration_fallback"}

    pairs = [(h["patients_ahead"], h["actual_wait_minutes"]) for h in history]
    n = len(pairs)
    sx  = sum(p[0] for p in pairs); sy  = sum(p[1] for p in pairs)
    sxy = sum(p[0]*p[1] for p in pairs); sx2 = sum(p[0]**2 for p in pairs)
    denom = n * sx2 - sx * sx
    slope = ((n * sxy - sx * sy) / denom) if denom else (sy / sx if sx else 20)
    intercept = (sy - slope * sx) / n if n else 0
    predicted = max(0, int(slope * patients_ahead + intercept))
    return {"predicted_minutes": predicted,
            "confidence": "high" if n >= 5 else "medium" if n >= 2 else "low",
            "data_points": n, "method": "linear_regression"}


def _generate_time_slots(start: str, end: str, duration_min: int) -> list[str]:
    s = datetime.strptime(start, "%H:%M")
    e = datetime.strptime(end,   "%H:%M")
    d = timedelta(minutes=duration_min)
    slots, cur = [], s
    while cur + d <= e:
        slots.append(cur.strftime("%H:%M"))
        cur += d
    return slots


# ── Schemas ────────────────────────────────────────────────────────────────────
class SymptomRequest(BaseModel):
    symptoms: str
    age: Optional[int] = None
    gender: Optional[str] = None

class SmartQueueRequest(BaseModel):
    doctor_id: str
    date: Optional[str] = None

class SmartSlotsRequest(BaseModel):
    doctor_id: str
    date: str


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("/symptom-check")
def symptom_check(req: SymptomRequest):
    if not req.symptoms or len(req.symptoms.strip()) < 3:
        return {"suggestions": [], "message": "Please describe your symptoms in more detail."}
    suggestions = _check_symptoms(req.symptoms)
    return {
        "query": req.symptoms,
        "suggestions": suggestions,
        "top_recommendation": suggestions[0] if suggestions else None,
        "disclaimer": "AI-assisted suggestion only. Consult a doctor for proper diagnosis.",
    }


@router.post("/smart-queue")
def smart_queue(req: SmartQueueRequest):
    target_date = req.date or date.today().isoformat()
    key = f"{req.doctor_id}:{target_date}"
    q_state = queue_state_db.get(key, {"current_token": 0})
    doctor  = next((d for d in doctors_db if d["id"] == req.doctor_id), None)
    if not doctor:
        return {"error": "Doctor not found"}

    waiting = [a for a in appointments_db
               if a["doctor_id"] == req.doctor_id
               and a["date"] == target_date
               and a["status"] == "waiting"]
    patients_ahead = len(waiting)
    prediction = _predict_wait(req.doctor_id, patients_ahead)
    return {
        "doctor_id": req.doctor_id, "doctor_name": doctor["name"],
        "date": target_date,
        "current_token": q_state.get("current_token", 0),
        "patients_ahead": patients_ahead,
        **prediction,
        "human_readable": f"~{prediction['predicted_minutes']} min wait" if prediction["predicted_minutes"] else "No wait",
    }


@router.post("/smart-slots")
def smart_slots(req: SmartSlotsRequest):
    doctor = next((d for d in doctors_db if d["id"] == req.doctor_id), None)
    if not doctor:
        return {"slots": [], "error": "Doctor not found"}
    try:
        date_obj    = datetime.strptime(req.date, "%Y-%m-%d").date()
        day_of_week = date_obj.weekday()
    except Exception:
        return {"slots": [], "error": "Invalid date format"}

    avails    = [a for a in availability_db if a["doctor_id"] == req.doctor_id and a["day_of_week"] == day_of_week]
    all_slots = []
    for av in avails:
        for slot_time in _generate_time_slots(av["start_time"], av["end_time"], av["slot_duration_minutes"]):
            booked = len([a for a in appointments_db
                          if a["doctor_id"] == req.doctor_id and a["date"] == req.date
                          and a["time_slot"] == slot_time and a["status"] != "cancelled"])
            load_pct = min(100, int(booked / av["max_patients"] * 100))
            all_slots.append({
                "time": slot_time, "availability_id": av["id"],
                "available": booked < av["max_patients"],
                "booked_count": booked, "max_patients": av["max_patients"],
                "load_percentage": load_pct,
                "crowd_level": "high" if load_pct >= 70 else "medium" if load_pct >= 30 else "low",
                "recommended": load_pct < 30,
            })

    all_slots.sort(key=lambda s: (not s["available"], s["load_percentage"]))
    return {
        "doctor_id": req.doctor_id, "doctor_name": doctor["name"],
        "date": req.date, "slots": all_slots,
        "best_slot": next((s["time"] for s in all_slots if s["recommended"]), None),
    }


@router.get("/insights")
def get_insights():
    today     = date.today().isoformat()
    today_apts = [a for a in appointments_db if a["date"] == today]
    completed  = [a for a in today_apts if a["status"] == "completed"]
    waiting    = [a for a in today_apts if a["status"] == "waiting"]
    throughput = len(completed) / max(len(today_apts), 1) * 100

    peak_h: dict[str, int] = {}
    for a in today_apts:
        h = a["time_slot"][:2]
        peak_h[h] = peak_h.get(h, 0) + 1
    peak_hour = (max(peak_h, key=lambda k: peak_h[k]) + ":00") if peak_h else "N/A"

    efficiency = []
    for d in doctors_db:
        d_apts = [a for a in today_apts if a["doctor_id"] == d["id"]]
        d_done = [a for a in d_apts if a["status"] == "completed"]
        if d_apts:
            efficiency.append({"doctor": d["name"], "total": len(d_apts),
                                "completed": len(d_done),
                                "efficiency_pct": round(len(d_done)/len(d_apts)*100)})

    return {
        "date": today, "total_appointments": len(today_apts),
        "completed": len(completed), "waiting": len(waiting),
        "throughput_pct": round(throughput, 1), "peak_hour": peak_hour,
        "doctor_efficiency": sorted(efficiency, key=lambda x: -x["efficiency_pct"]),
        "recommendation": ("Queue running smoothly." if throughput >= 70
                           else "High queue load — consider adding more slots."),
    }
