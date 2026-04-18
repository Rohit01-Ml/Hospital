# MediCare+ Hospital Management System

A production-ready MVP with Angular frontend and FastAPI backend (mock data).

## Quick Start

### 1. Start Backend
Double-click `start-backend.bat` **or** run:
```bash
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs

### 2. Start Frontend
Double-click `start-frontend.bat` **or** run:
```bash
cd frontend
npm install
npm start
```
Frontend: http://localhost:4200

---

## Demo Credentials

| Role    | Email                | Password |
|---------|----------------------|----------|
| Admin   | admin@hospital.com   | secret   |
| Patient | john@example.com     | secret   |
| Patient | jane@example.com     | secret   |

Use the **Quick Demo** buttons on the login page.

---

## Features

### Patient
- Landing page with auto slideshow
- Register / Login / Google OAuth (mock)
- Book appointment: Specialization → Doctor → Date → Time slot
- View all appointments with status badges
- Live queue tracking (auto-refreshes every 15s)
- Token number, current token, patients ahead display

### Admin
- Dashboard with real-time stats
- Doctor CRUD (add, edit, delete, toggle availability)
- Specialization CRUD with icon picker
- Queue control: Next / Skip / Complete buttons
- Auto-refreshing queue table

---

## Architecture

```
hospital/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + CORS
│   │   ├── mock_data.py         # In-memory data stores
│   │   ├── dependencies.py      # JWT auth dependency
│   │   ├── auth/                # Register, Login, Google OAuth
│   │   ├── doctors/             # Doctor + Availability CRUD
│   │   ├── specializations/     # Specialization CRUD
│   │   ├── appointments/        # Booking + token assignment
│   │   └── queue/               # Queue state management
│   └── requirements.txt
└── frontend/
    └── src/app/
        ├── core/                # Auth service, interceptor, guards
        ├── shared/models/       # TypeScript interfaces
        └── features/
            ├── landing/         # Hero slideshow + info
            ├── auth/            # Login + Register
            ├── patient/         # Dashboard, Book, Appointments, Queue
            └── admin/           # Dashboard, Doctors, Specs, Queue

```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register user |
| POST | /auth/login | Login |
| POST | /auth/google | Google OAuth (mock) |
| GET | /auth/me | Current user |
| GET | /specializations/ | List all |
| POST | /specializations/ | Create (admin) |
| GET | /doctors/ | List (filter by spec) |
| GET | /doctors/{id}/slots?date_str= | Available slots |
| GET | /appointments/ | List appointments |
| POST | /appointments/ | Book appointment |
| DELETE | /appointments/{id} | Cancel |
| GET | /queue/{doctor_id} | Queue status |
| GET | /queue/{doctor_id}/my-status | Patient queue position |
| POST | /queue/{doctor_id}/next | Next patient (admin) |
| POST | /queue/{doctor_id}/skip/{apt_id} | Skip patient (admin) |
| POST | /queue/{doctor_id}/complete/{apt_id} | Mark complete (admin) |
