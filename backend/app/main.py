import asyncio
import os
from datetime import date
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request

# Load .env before anything else
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed — use system env vars
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# ── Routers ────────────────────────────────────────────────────────────────────
from app.auth.router             import router as auth_router
from app.specializations.router  import router as spec_router
from app.doctors.router          import router as doctors_router
from app.appointments.router     import router as appointments_router
from app.queue.router            import router as queue_router
from app.payments.router         import router as payments_router
from app.prescriptions.router    import router as prescriptions_router
from app.lab_tests.router        import router as lab_tests_router
from app.reports.router          import router as reports_router
from app.notifications.router    import router as notifications_router
from app.medicine_reminders.router import router as medicine_router
# Stage 3 — SaaS
from app.hospitals.router        import router as hospitals_router
from app.ai.router               import router as ai_router
from app.doctor_portal.router    import router as doctor_router
from app.receptionist.router     import router as receptionist_router

from app.websocket_manager import manager
from app.mock_data import appointments_db, queue_state_db

# ── Rate limiter ───────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="MediCare+ SaaS Hospital Platform",
    description="""
    **Stage 3 — SaaS Multi-Tenant Platform**

    ### New in Stage 3:
    - Multi-Tenant Architecture (hospital_id isolation)
    - Doctor Role & Portal
    - AI Symptom Checker
    - Smart Queue Prediction
    - Smart Slot Recommendation
    - Live Queue WebSockets
    - Rate Limiting
    - RBAC (Patient / Doctor / Admin)

    ### Demo Credentials:
    | Role    | Email                    | Password |
    |---------|--------------------------|----------|
    | Admin   | admin@hospital.com       | secret   |
    | Patient | john@example.com         | secret   |
    | Doctor  | sarah.j@hospital.com     | secret   |
    | Doctor  | david.t@hospital.com     | secret   |
    | Receptionist | riya@hospital.com   | secret   |
    """,
    version="3.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Stage 1 ────────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(spec_router)
app.include_router(doctors_router)
app.include_router(appointments_router)
app.include_router(queue_router)
# ── Stage 2 ────────────────────────────────────────────────────────────────────
app.include_router(payments_router)
app.include_router(prescriptions_router)
app.include_router(lab_tests_router)
app.include_router(reports_router)
app.include_router(notifications_router)
app.include_router(medicine_router)
# ── Stage 3 — SaaS ─────────────────────────────────────────────────────────────
app.include_router(hospitals_router)
app.include_router(ai_router)
app.include_router(doctor_router)
app.include_router(receptionist_router)


# ── WebSocket — Live Queue ─────────────────────────────────────────────────────
@app.websocket("/ws/queue/{doctor_id}")
async def queue_websocket(websocket: WebSocket, doctor_id: str):
    await manager.connect(websocket, doctor_id)
    try:
        while True:
            # Send a queue snapshot every 5 seconds
            await asyncio.sleep(5)
            today = date.today().isoformat()
            apts  = [a for a in appointments_db
                     if a["doctor_id"] == doctor_id and a["date"] == today]
            q     = queue_state_db.get(f"{doctor_id}:{today}", {"current_token": 0})
            await manager.broadcast(doctor_id, {
                "type": "queue_update",
                "doctor_id": doctor_id,
                "current_token": q.get("current_token", 0),
                "total_patients": len([a for a in apts if a["status"] != "cancelled"]),
                "waiting":     len([a for a in apts if a["status"] == "waiting"]),
                "in_progress": len([a for a in apts if a["status"] == "in_progress"]),
                "completed":   len([a for a in apts if a["status"] == "completed"]),
            })
    except (WebSocketDisconnect, Exception):
        manager.disconnect(websocket, doctor_id)


# ── Root ───────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {
        "app": "MediCare+ SaaS Hospital Platform",
        "version": "3.0.0",
        "docs": "/docs",
        "features": ["multi-tenant", "ai", "websocket", "rbac", "rate-limiting"],
    }

@app.get("/health", tags=["Root"])
def health():
    return {"status": "healthy", "version": "3.0.0"}
