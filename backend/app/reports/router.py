from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.reports.schemas import ReportCreate, ReportUpdate
from app.mock_data import reports_db, lab_test_types_db, lab_bookings_db, users_db, notifications_db, next_id
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/reports", tags=["Reports"])

def _enrich(r: dict) -> dict:
    test_type = next((t for t in lab_test_types_db if t["id"] == r.get("test_type_id")), None)
    patient   = next((u for u in users_db if u["id"] == r["patient_id"]), None)
    return {**r, "test_type": test_type, "patient_name": patient["name"] if patient else "Unknown"}

def _notify_report_upload(patient_id: str, title: str):
    notifications_db.append({
        "id": next_id("notification"),
        "user_id": patient_id,
        "type": "report_ready",
        "title": "New Report Available",
        "message": f"Your report '{title}' has been uploaded and is ready to view.",
        "read": False,
        "action_url": "/patient/reports",
        "created_at": datetime.utcnow().isoformat(),
    })

@router.get("/")
def list_reports(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "admin":
        return [_enrich(r) for r in reports_db]
    return [_enrich(r) for r in reports_db if r["patient_id"] == current_user["id"]]

@router.get("/{report_id}")
def get_report(report_id: str, current_user: dict = Depends(get_current_user)):
    r = next((x for x in reports_db if x["id"] == report_id), None)
    if not r:
        raise HTTPException(404, "Report not found")
    if current_user["role"] != "admin" and r["patient_id"] != current_user["id"]:
        raise HTTPException(403, "Not authorized")
    return _enrich(r)

@router.post("/", dependencies=[Depends(require_admin)])
def upload_report(req: ReportCreate, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    r = {
        "id": next_id("report"),
        "patient_id": req.patient_id,
        "lab_booking_id": req.lab_booking_id,
        "test_type_id": req.test_type_id,
        "title": req.title,
        "findings": req.findings,
        "interpretation": req.interpretation or "",
        "status": req.status,
        "file_url": req.file_url or f"mock://reports/{next_id('report')}.pdf",
        "uploaded_by": current_user["id"],
        "created_at": datetime.utcnow().isoformat(),
    }
    reports_db.append(r)

    # Update lab booking status if linked
    if req.lab_booking_id:
        lb = next((b for b in lab_bookings_db if b["id"] == req.lab_booking_id), None)
        if lb:
            lb["status"] = "report_ready"

    background_tasks.add_task(_notify_report_upload, req.patient_id, req.title)
    return _enrich(r)

@router.put("/{report_id}", dependencies=[Depends(require_admin)])
def update_report(report_id: str, req: ReportUpdate):
    r = next((x for x in reports_db if x["id"] == report_id), None)
    if not r:
        raise HTTPException(404, "Report not found")
    r.update(req.model_dump(exclude_none=True))
    return _enrich(r)

@router.delete("/{report_id}", dependencies=[Depends(require_admin)])
def delete_report(report_id: str):
    r = next((x for x in reports_db if x["id"] == report_id), None)
    if not r:
        raise HTTPException(404, "Report not found")
    reports_db[:] = [x for x in reports_db if x["id"] != report_id]
    return {"message": "Report deleted"}

@router.get("/{report_id}/download")
def download_report(report_id: str, current_user: dict = Depends(get_current_user)):
    r = next((x for x in reports_db if x["id"] == report_id), None)
    if not r:
        raise HTTPException(404, "Report not found")
    if current_user["role"] != "admin" and r["patient_id"] != current_user["id"]:
        raise HTTPException(403, "Not authorized")
    return {
        "download_url": r.get("file_url", f"mock://reports/{report_id}.pdf"),
        "filename": f"report_{report_id}.pdf",
        "report": _enrich(r),
    }
