from datetime import date, datetime

today_str    = date.today().isoformat()
yesterday    = "2024-12-10"
two_days_ago = "2024-12-09"

# ── Helpers ────────────────────────────────────────────────────────────────────
# For mock data we store passwords as plain text prefixed with "plain:"
# The auth service checks this prefix and compares directly — no bcrypt needed.
_SECRET_HASH = "plain:secret"

# ── Hospitals (Multi-Tenant) ───────────────────────────────────────────────────
hospitals_db = [
    {
        "id": "h1", "name": "City General Hospital", "slug": "city-general",
        "subscription": "enterprise", "admin_email": "admin@hospital.com",
        "phone": "+917075886985", "address": "123 Medical Drive, Downtown",
        "logo_url": None, "active": True, "created_at": "2024-01-01",
        "plan_features": ["unlimited_doctors", "ai_features", "websocket", "whatsapp"],
        "monthly_fee": 9999,
    },
    {
        "id": "h2", "name": "Metro Healthcare", "slug": "metro-health",
        "subscription": "professional", "admin_email": "metro@hospital.com",
        "phone": "+1-555-2000", "address": "456 Health Avenue, Metro City",
        "logo_url": None, "active": True, "created_at": "2024-02-01",
        "plan_features": ["up_to_20_doctors", "ai_features"],
        "monthly_fee": 4999,
    },
]

# ── Users ──────────────────────────────────────────────────────────────────────
users_db = [
    # Admin
    {"id": "u1",  "name": "Admin User",          "email": "admin@hospital.com",    "password_hash": _SECRET_HASH, "role": "admin",   "hospital_id": "h1", "doctor_id": None, "created_at": "2024-01-01"},
    # Patients
    {"id": "u2",  "name": "John Patient",         "email": "john@example.com",      "password_hash": _SECRET_HASH, "role": "patient", "hospital_id": "h1", "doctor_id": None, "phone": "+917989971159", "age": 45, "gender": "Male",   "blood_group": "O+", "address": "42 Park Street, Mumbai",  "created_at": "2024-01-10"},
    {"id": "u3",  "name": "Jane Smith",            "email": "jane@example.com",      "password_hash": _SECRET_HASH, "role": "patient", "hospital_id": "h1", "doctor_id": None, "phone": None,            "age": 32, "gender": "Female", "blood_group": "A-", "address": "7 Hill View, Pune",        "created_at": "2024-01-15"},
    {"id": "u4",  "name": "Bob Wilson",            "email": "bob@example.com",       "password_hash": _SECRET_HASH, "role": "patient", "hospital_id": "h1", "doctor_id": None, "phone": None,            "age": 58, "gender": "Male",   "blood_group": "B+", "address": "19 Lake Road, Hyderabad",  "created_at": "2024-02-01"},
    # Neurology patients (for Amit Verma rc3 / s3)
    {"id": "u5",  "name": "Arjun Mehta",           "email": "arjun@example.com",     "password_hash": _SECRET_HASH, "role": "patient", "hospital_id": "h1", "doctor_id": None, "phone": "+919876543210", "age": 42, "gender": "Male",   "blood_group": "B+", "address": "12 MG Road, Bangalore", "created_at": "2024-03-01"},
    {"id": "u6",  "name": "Kavya Rao",             "email": "kavya@example.com",     "password_hash": _SECRET_HASH, "role": "patient", "hospital_id": "h1", "doctor_id": None, "phone": "+919845678901", "age": 35, "gender": "Female", "blood_group": "O+", "address": "55 Anna Nagar, Chennai",  "created_at": "2024-03-05"},
    # Orthopedics extra patients (for Priya Nair rc2 / s2 — doctor d4)
    {"id": "u7",  "name": "Rahul Gupta",           "email": "rahul@example.com",     "password_hash": _SECRET_HASH, "role": "patient", "hospital_id": "h1", "doctor_id": None, "phone": "+919823456789", "age": 55, "gender": "Male",   "blood_group": "A+", "address": "88 Civil Lines, Delhi",   "created_at": "2024-03-10"},
    # Doctor users (linked to doctor records)
    {"id": "du1", "name": "Dr. Sarah Johnson",     "email": "sarah.j@hospital.com",  "password_hash": _SECRET_HASH, "role": "doctor",  "hospital_id": "h1", "doctor_id": "d1", "created_at": "2024-01-01"},
    {"id": "du2", "name": "Dr. Michael Chen",      "email": "michael.c@hospital.com","password_hash": _SECRET_HASH, "role": "doctor",  "hospital_id": "h1", "doctor_id": "d2", "created_at": "2024-01-01"},
    {"id": "du3", "name": "Dr. Emily Rodriguez",   "email": "emily.r@hospital.com",  "password_hash": _SECRET_HASH, "role": "doctor",  "hospital_id": "h1", "doctor_id": "d3", "created_at": "2024-01-01"},
    {"id": "du4", "name": "Dr. David Thompson",    "email": "david.t@hospital.com",  "password_hash": _SECRET_HASH, "role": "doctor",  "hospital_id": "h1", "doctor_id": "d8", "created_at": "2024-01-01"},
    # Receptionists — each assigned to one department (specialization_id)
    {"id": "rc1", "name": "Riya Sharma",      "email": "riya@hospital.com",    "password_hash": _SECRET_HASH, "role": "receptionist", "hospital_id": "h1", "doctor_id": None, "phone": None, "specialization_id": "s1", "created_at": "2024-01-01"},  # Cardiology
    {"id": "rc2", "name": "Priya Nair",       "email": "priya@hospital.com",   "password_hash": _SECRET_HASH, "role": "receptionist", "hospital_id": "h1", "doctor_id": None, "phone": None, "specialization_id": "s2", "created_at": "2024-01-01"},  # Orthopedics
    {"id": "rc3", "name": "Amit Verma",       "email": "amit@hospital.com",    "password_hash": _SECRET_HASH, "role": "receptionist", "hospital_id": "h1", "doctor_id": None, "phone": None, "specialization_id": "s3", "created_at": "2024-01-01"},  # Neurology
    {"id": "rc4", "name": "Sneha Patel",      "email": "sneha@hospital.com",   "password_hash": _SECRET_HASH, "role": "receptionist", "hospital_id": "h1", "doctor_id": None, "phone": None, "specialization_id": "s6", "created_at": "2024-01-01"},  # General Medicine
]

# ── Specializations ────────────────────────────────────────────────────────────
specializations_db = [
    {"id": "s1", "name": "Cardiology",       "description": "Heart and cardiovascular system",           "icon": "favorite",          "hospital_id": "h1"},
    {"id": "s2", "name": "Orthopedics",      "description": "Bones, joints and musculoskeletal system",  "icon": "accessibility_new", "hospital_id": "h1"},
    {"id": "s3", "name": "Neurology",        "description": "Brain and nervous system disorders",        "icon": "psychology",        "hospital_id": "h1"},
    {"id": "s4", "name": "Dermatology",      "description": "Skin, hair and nail conditions",            "icon": "spa",               "hospital_id": "h1"},
    {"id": "s5", "name": "Pediatrics",       "description": "Medical care for infants and children",     "icon": "child_care",        "hospital_id": "h1"},
    {"id": "s6", "name": "General Medicine", "description": "Primary healthcare and general conditions", "icon": "local_hospital",    "hospital_id": "h1"},
]

# ── Doctors ────────────────────────────────────────────────────────────────────
doctors_db = [
    {"id": "d1", "name": "Dr. Sarah Johnson",   "specialization_id": "s1", "experience_years": 12, "qualification": "MD, FACC",        "phone": "+1-555-0101", "email": "sarah.j@hospital.com",   "bio": "Renowned cardiologist with expertise in interventional cardiology.",         "rating": 4.8, "patients_treated": 3200, "image_url": None, "available": True, "hospital_id": "h1"},
    {"id": "d2", "name": "Dr. Michael Chen",    "specialization_id": "s1", "experience_years": 8,  "qualification": "MD, PhD",          "phone": "+1-555-0102", "email": "michael.c@hospital.com", "bio": "Specialist in cardiac electrophysiology and arrhythmia management.",         "rating": 4.6, "patients_treated": 1800, "image_url": None, "available": True, "hospital_id": "h1"},
    {"id": "d3", "name": "Dr. Emily Rodriguez", "specialization_id": "s2", "experience_years": 15, "qualification": "MD, FAAOS",        "phone": "+1-555-0103", "email": "emily.r@hospital.com",   "bio": "Expert in joint replacement surgery and sports medicine.",                   "rating": 4.9, "patients_treated": 4100, "image_url": None, "available": True, "hospital_id": "h1"},
    {"id": "d4", "name": "Dr. James Wilson",    "specialization_id": "s2", "experience_years": 10, "qualification": "MD, MS Ortho",     "phone": "+1-555-0104", "email": "james.w@hospital.com",   "bio": "Specializes in spine surgery and minimally invasive orthopedic procedures.", "rating": 4.7, "patients_treated": 2500, "image_url": None, "available": True, "hospital_id": "h1"},
    {"id": "d5", "name": "Dr. Priya Patel",     "specialization_id": "s3", "experience_years": 11, "qualification": "MD, DM Neurology", "phone": "+1-555-0105", "email": "priya.p@hospital.com",   "bio": "Neurologist specializing in stroke management and epilepsy treatment.",      "rating": 4.8, "patients_treated": 2900, "image_url": None, "available": True, "hospital_id": "h1"},
    {"id": "d6", "name": "Dr. Robert Kim",      "specialization_id": "s4", "experience_years": 9,  "qualification": "MD, FAAD",         "phone": "+1-555-0106", "email": "robert.k@hospital.com",  "bio": "Expert in cosmetic dermatology and skin cancer treatment.",                  "rating": 4.5, "patients_treated": 3600, "image_url": None, "available": True, "hospital_id": "h1"},
    {"id": "d7", "name": "Dr. Lisa Anderson",   "specialization_id": "s5", "experience_years": 14, "qualification": "MD, FAAP",         "phone": "+1-555-0107", "email": "lisa.a@hospital.com",    "bio": "Dedicated pediatrician with focus on child developmental health.",           "rating": 4.9, "patients_treated": 5200, "image_url": None, "available": True, "hospital_id": "h1"},
    {"id": "d8", "name": "Dr. David Thompson",  "specialization_id": "s6", "experience_years": 20, "qualification": "MD, MBBS",         "phone": "+1-555-0108", "email": "david.t@hospital.com",   "bio": "Experienced general physician providing comprehensive primary care.",        "rating": 4.7, "patients_treated": 7800, "image_url": None, "available": True, "hospital_id": "h1"},
]

# ── Availability (Mon=0 … Fri=4, all doctors available Mon–Fri) ────────────────
# Each doctor has slots every weekday so booking works on any date the user picks.
availability_db = [
    # d1 — Dr. Sarah Johnson (Cardiology) — 20-min slots, 09:00–13:00
    {"id": "av1",  "doctor_id": "d1", "day_of_week": 0, "start_time": "09:00", "end_time": "13:00", "slot_duration_minutes": 20, "max_patients": 12},
    {"id": "av2",  "doctor_id": "d1", "day_of_week": 1, "start_time": "09:00", "end_time": "13:00", "slot_duration_minutes": 20, "max_patients": 12},
    {"id": "av3",  "doctor_id": "d1", "day_of_week": 2, "start_time": "14:00", "end_time": "18:00", "slot_duration_minutes": 20, "max_patients": 12},
    {"id": "av4",  "doctor_id": "d1", "day_of_week": 3, "start_time": "09:00", "end_time": "13:00", "slot_duration_minutes": 20, "max_patients": 12},
    {"id": "av5",  "doctor_id": "d1", "day_of_week": 4, "start_time": "09:00", "end_time": "13:00", "slot_duration_minutes": 20, "max_patients": 12},
    # d2 — Dr. Michael Chen (Cardiology) — 20-min slots, 10:00–14:00
    {"id": "av6",  "doctor_id": "d2", "day_of_week": 0, "start_time": "10:00", "end_time": "14:00", "slot_duration_minutes": 20, "max_patients": 12},
    {"id": "av7",  "doctor_id": "d2", "day_of_week": 1, "start_time": "10:00", "end_time": "14:00", "slot_duration_minutes": 20, "max_patients": 12},
    {"id": "av8",  "doctor_id": "d2", "day_of_week": 2, "start_time": "10:00", "end_time": "14:00", "slot_duration_minutes": 20, "max_patients": 12},
    {"id": "av9",  "doctor_id": "d2", "day_of_week": 3, "start_time": "10:00", "end_time": "14:00", "slot_duration_minutes": 20, "max_patients": 12},
    {"id": "av10", "doctor_id": "d2", "day_of_week": 4, "start_time": "10:00", "end_time": "14:00", "slot_duration_minutes": 20, "max_patients": 12},
    # d3 — Dr. Emily Rodriguez (Orthopedics) — 30-min slots, 08:00–13:00
    {"id": "av11", "doctor_id": "d3", "day_of_week": 0, "start_time": "08:00", "end_time": "13:00", "slot_duration_minutes": 30, "max_patients": 10},
    {"id": "av12", "doctor_id": "d3", "day_of_week": 1, "start_time": "08:00", "end_time": "13:00", "slot_duration_minutes": 30, "max_patients": 10},
    {"id": "av13", "doctor_id": "d3", "day_of_week": 2, "start_time": "08:00", "end_time": "13:00", "slot_duration_minutes": 30, "max_patients": 10},
    {"id": "av14", "doctor_id": "d3", "day_of_week": 3, "start_time": "13:00", "end_time": "17:00", "slot_duration_minutes": 30, "max_patients": 8},
    {"id": "av15", "doctor_id": "d3", "day_of_week": 4, "start_time": "08:00", "end_time": "13:00", "slot_duration_minutes": 30, "max_patients": 10},
    # d4 — Dr. James Wilson (Orthopedics) — 30-min slots, 09:00–17:00
    {"id": "av16", "doctor_id": "d4", "day_of_week": 0, "start_time": "09:00", "end_time": "17:00", "slot_duration_minutes": 30, "max_patients": 16},
    {"id": "av17", "doctor_id": "d4", "day_of_week": 1, "start_time": "09:00", "end_time": "17:00", "slot_duration_minutes": 30, "max_patients": 16},
    {"id": "av18", "doctor_id": "d4", "day_of_week": 2, "start_time": "09:00", "end_time": "17:00", "slot_duration_minutes": 30, "max_patients": 16},
    {"id": "av19", "doctor_id": "d4", "day_of_week": 3, "start_time": "09:00", "end_time": "17:00", "slot_duration_minutes": 30, "max_patients": 16},
    {"id": "av20", "doctor_id": "d4", "day_of_week": 4, "start_time": "09:00", "end_time": "13:00", "slot_duration_minutes": 30, "max_patients": 8},
    # d5 — Dr. Priya Patel (Neurology) — 25-min slots, 09:00–14:00
    {"id": "av21", "doctor_id": "d5", "day_of_week": 0, "start_time": "09:00", "end_time": "14:00", "slot_duration_minutes": 25, "max_patients": 12},
    {"id": "av22", "doctor_id": "d5", "day_of_week": 1, "start_time": "09:00", "end_time": "14:00", "slot_duration_minutes": 25, "max_patients": 12},
    {"id": "av23", "doctor_id": "d5", "day_of_week": 2, "start_time": "09:00", "end_time": "14:00", "slot_duration_minutes": 25, "max_patients": 12},
    {"id": "av24", "doctor_id": "d5", "day_of_week": 3, "start_time": "09:00", "end_time": "14:00", "slot_duration_minutes": 25, "max_patients": 12},
    {"id": "av25", "doctor_id": "d5", "day_of_week": 4, "start_time": "14:00", "end_time": "18:00", "slot_duration_minutes": 25, "max_patients": 10},
    # d6 — Dr. Robert Kim (Dermatology) — 20-min slots, 10:00–16:00
    {"id": "av26", "doctor_id": "d6", "day_of_week": 0, "start_time": "10:00", "end_time": "16:00", "slot_duration_minutes": 20, "max_patients": 18},
    {"id": "av27", "doctor_id": "d6", "day_of_week": 1, "start_time": "10:00", "end_time": "16:00", "slot_duration_minutes": 20, "max_patients": 18},
    {"id": "av28", "doctor_id": "d6", "day_of_week": 2, "start_time": "10:00", "end_time": "16:00", "slot_duration_minutes": 20, "max_patients": 18},
    {"id": "av29", "doctor_id": "d6", "day_of_week": 3, "start_time": "10:00", "end_time": "16:00", "slot_duration_minutes": 20, "max_patients": 18},
    {"id": "av30", "doctor_id": "d6", "day_of_week": 4, "start_time": "10:00", "end_time": "14:00", "slot_duration_minutes": 20, "max_patients": 12},
    # d7 — Dr. Lisa Anderson (Pediatrics) — 15-min slots, 09:00–17:00
    {"id": "av31", "doctor_id": "d7", "day_of_week": 0, "start_time": "09:00", "end_time": "17:00", "slot_duration_minutes": 15, "max_patients": 20},
    {"id": "av32", "doctor_id": "d7", "day_of_week": 1, "start_time": "09:00", "end_time": "17:00", "slot_duration_minutes": 15, "max_patients": 20},
    {"id": "av33", "doctor_id": "d7", "day_of_week": 2, "start_time": "09:00", "end_time": "17:00", "slot_duration_minutes": 15, "max_patients": 20},
    {"id": "av34", "doctor_id": "d7", "day_of_week": 3, "start_time": "09:00", "end_time": "17:00", "slot_duration_minutes": 15, "max_patients": 20},
    {"id": "av35", "doctor_id": "d7", "day_of_week": 4, "start_time": "09:00", "end_time": "17:00", "slot_duration_minutes": 15, "max_patients": 20},
    # d8 — Dr. David Thompson (General Medicine) — 15-min slots, 08:00–20:00
    {"id": "av36", "doctor_id": "d8", "day_of_week": 0, "start_time": "08:00", "end_time": "20:00", "slot_duration_minutes": 15, "max_patients": 30},
    {"id": "av37", "doctor_id": "d8", "day_of_week": 1, "start_time": "08:00", "end_time": "20:00", "slot_duration_minutes": 15, "max_patients": 30},
    {"id": "av38", "doctor_id": "d8", "day_of_week": 2, "start_time": "08:00", "end_time": "20:00", "slot_duration_minutes": 15, "max_patients": 30},
    {"id": "av39", "doctor_id": "d8", "day_of_week": 3, "start_time": "08:00", "end_time": "20:00", "slot_duration_minutes": 15, "max_patients": 30},
    {"id": "av40", "doctor_id": "d8", "day_of_week": 4, "start_time": "08:00", "end_time": "20:00", "slot_duration_minutes": 15, "max_patients": 30},
]

# ── Appointments ───────────────────────────────────────────────────────────────
appointments_db = [
    {"id": "apt1", "patient_id": "u2", "doctor_id": "d1", "specialization_id": "s1", "date": today_str, "time_slot": "09:00", "token_number": 1, "status": "completed",   "notes": "Follow-up on hypertension",  "estimated_wait": 0,  "hospital_id": "h1"},
    {"id": "apt2", "patient_id": "u3", "doctor_id": "d1", "specialization_id": "s1", "date": today_str, "time_slot": "09:20", "token_number": 2, "status": "in_progress", "notes": "Chest pain evaluation",      "estimated_wait": 0,  "hospital_id": "h1"},
    {"id": "apt3", "patient_id": "u4", "doctor_id": "d1", "specialization_id": "s1", "date": today_str, "time_slot": "09:40", "token_number": 3, "status": "waiting",     "notes": "ECG results review",         "estimated_wait": 20, "hospital_id": "h1"},
    {"id": "apt4", "patient_id": "u2", "doctor_id": "d1", "specialization_id": "s1", "date": today_str, "time_slot": "10:00", "token_number": 4, "status": "waiting",     "notes": "",                           "estimated_wait": 40, "hospital_id": "h1"},
    {"id": "apt5", "patient_id": "u3", "doctor_id": "d3", "specialization_id": "s2", "date": today_str, "time_slot": "08:00", "token_number": 1, "status": "completed",   "notes": "Knee pain assessment",       "estimated_wait": 0,  "hospital_id": "h1"},
    {"id": "apt6", "patient_id": "u2", "doctor_id": "d8", "specialization_id": "s6", "date": today_str, "time_slot": "08:00", "token_number": 1, "status": "completed",   "notes": "Annual checkup",             "estimated_wait": 0,  "hospital_id": "h1"},
    {"id": "apt7", "patient_id": "u4", "doctor_id": "d8", "specialization_id": "s6", "date": today_str, "time_slot": "08:15", "token_number": 2, "status": "waiting",     "notes": "Fever and cold",             "estimated_wait": 15, "hospital_id": "h1"},
    # Neurology — Dr. Priya Patel (d5 / s3) → for Amit Verma (rc3)
    {"id": "apt8",  "patient_id": "u5", "doctor_id": "d5", "specialization_id": "s3", "date": today_str, "time_slot": "09:00", "token_number": 1, "status": "in_progress", "notes": "Severe migraine episodes",      "priority": False, "estimated_wait": 0,  "hospital_id": "h1"},
    {"id": "apt9",  "patient_id": "u6", "doctor_id": "d5", "specialization_id": "s3", "date": today_str, "time_slot": "09:20", "token_number": 2, "status": "waiting",     "notes": "Numbness in left arm",          "priority": True,  "estimated_wait": 20, "hospital_id": "h1"},
    {"id": "apt10", "patient_id": "u2", "doctor_id": "d5", "specialization_id": "s3", "date": today_str, "time_slot": "09:40", "token_number": 3, "status": "waiting",     "notes": "Follow-up EEG review",          "priority": False, "estimated_wait": 40, "hospital_id": "h1"},
    # Orthopedics — Dr. James Wilson (d4 / s2) → for Priya Nair (rc2)
    {"id": "apt11", "patient_id": "u7", "doctor_id": "d4", "specialization_id": "s2", "date": today_str, "time_slot": "09:00", "token_number": 1, "status": "in_progress", "notes": "Lower back pain, MRI required", "priority": False, "estimated_wait": 0,  "hospital_id": "h1"},
    {"id": "apt12", "patient_id": "u2", "doctor_id": "d4", "specialization_id": "s2", "date": today_str, "time_slot": "09:30", "token_number": 2, "status": "waiting",     "notes": "Post-op knee review",           "priority": False, "estimated_wait": 30, "hospital_id": "h1"},
    # General Medicine — Dr. David Thompson (d8 / s6) extra patient → for Sneha Patel (rc4)
    {"id": "apt13", "patient_id": "u3", "doctor_id": "d8", "specialization_id": "s6", "date": today_str, "time_slot": "09:00", "token_number": 3, "status": "waiting",     "notes": "Diabetes follow-up",           "priority": False, "estimated_wait": 30, "hospital_id": "h1"},
]

# ── Queue State ────────────────────────────────────────────────────────────────
queue_state_db: dict = {
    f"d1:{today_str}": {"current_token": 2, "doctor_id": "d1", "date": today_str},
    f"d3:{today_str}": {"current_token": 1, "doctor_id": "d3", "date": today_str},
    f"d8:{today_str}": {"current_token": 1, "doctor_id": "d8", "date": today_str},
    f"d5:{today_str}": {"current_token": 1, "doctor_id": "d5", "date": today_str},  # Neurology
    f"d4:{today_str}": {"current_token": 1, "doctor_id": "d4", "date": today_str},  # Orthopedics
}

# ── Queue History (for AI wait-time prediction) ───────────────────────────────
queue_history_db = [
    # doctor_id, date, slot, actual wait time (minutes), patient_count
    {"doctor_id": "d1", "date": yesterday,    "time_slot": "09:00", "actual_wait_minutes": 18, "patients_ahead": 1},
    {"doctor_id": "d1", "date": yesterday,    "time_slot": "09:20", "actual_wait_minutes": 22, "patients_ahead": 2},
    {"doctor_id": "d1", "date": yesterday,    "time_slot": "09:40", "actual_wait_minutes": 35, "patients_ahead": 3},
    {"doctor_id": "d1", "date": two_days_ago, "time_slot": "09:00", "actual_wait_minutes": 15, "patients_ahead": 1},
    {"doctor_id": "d1", "date": two_days_ago, "time_slot": "09:20", "actual_wait_minutes": 28, "patients_ahead": 2},
    {"doctor_id": "d1", "date": two_days_ago, "time_slot": "09:40", "actual_wait_minutes": 41, "patients_ahead": 3},
    {"doctor_id": "d8", "date": yesterday,    "time_slot": "08:00", "actual_wait_minutes": 12, "patients_ahead": 1},
    {"doctor_id": "d8", "date": yesterday,    "time_slot": "08:15", "actual_wait_minutes": 25, "patients_ahead": 2},
    {"doctor_id": "d8", "date": two_days_ago, "time_slot": "08:00", "actual_wait_minutes": 10, "patients_ahead": 1},
    {"doctor_id": "d3", "date": yesterday,    "time_slot": "08:00", "actual_wait_minutes": 28, "patients_ahead": 1},
]

# ── Slot Booking Counts (for smart slot recommendation) ──────────────────────
slot_booking_counts_db: dict = {
    # "doctor_id:date:time_slot" -> count
    f"d1:{today_str}:09:00": 1,
    f"d1:{today_str}:09:20": 1,
    f"d1:{today_str}:09:40": 1,
    f"d1:{today_str}:10:00": 1,
    f"d8:{today_str}:08:00": 1,
    f"d8:{today_str}:08:15": 1,
}

# ── Payments ───────────────────────────────────────────────────────────────────
payments_db = [
    {"id": "pay1", "appointment_id": "apt1", "patient_id": "u2", "amount": 500.00,  "currency": "INR", "status": "paid",    "razorpay_order_id": "order_mock_001", "razorpay_payment_id": "pay_mock_001", "method": "UPI",        "created_at": f"{today_str}T08:55:00", "hospital_id": "h1"},
    {"id": "pay2", "appointment_id": "apt5", "patient_id": "u3", "amount": 800.00,  "currency": "INR", "status": "paid",    "razorpay_order_id": "order_mock_002", "razorpay_payment_id": "pay_mock_002", "method": "Card",       "created_at": f"{today_str}T07:50:00", "hospital_id": "h1"},
    {"id": "pay3", "appointment_id": "apt6", "patient_id": "u2", "amount": 300.00,  "currency": "INR", "status": "paid",    "razorpay_order_id": "order_mock_003", "razorpay_payment_id": "pay_mock_003", "method": "NetBanking", "created_at": f"{today_str}T07:55:00", "hospital_id": "h1"},
    {"id": "pay4", "appointment_id": "apt4", "patient_id": "u2", "amount": 500.00,  "currency": "INR", "status": "pending", "razorpay_order_id": "order_mock_004", "razorpay_payment_id": None,           "method": None,         "created_at": f"{today_str}T09:50:00", "hospital_id": "h1"},
    {"id": "pay5", "appointment_id": "apt7", "patient_id": "u4", "amount": 300.00,  "currency": "INR", "status": "pending", "razorpay_order_id": "order_mock_005", "razorpay_payment_id": None,           "method": None,         "created_at": f"{today_str}T08:10:00", "hospital_id": "h1"},
]

# ── Prescriptions ──────────────────────────────────────────────────────────────
prescriptions_db = [
    {
        "id": "presc1", "appointment_id": "apt1", "patient_id": "u2", "doctor_id": "d1",
        "doctor_name": "Dr. Sarah Johnson",
        "diagnosis": "Stage 1 Hypertension",
        "medicines": [
            {"name": "Amlodipine", "dosage": "5mg",  "frequency": "Once daily", "duration": "30 days", "instructions": "Take in the morning"},
            {"name": "Losartan",   "dosage": "50mg",  "frequency": "Once daily", "duration": "30 days", "instructions": "Take with food"},
        ],
        "notes": "Reduce salt intake. Exercise 30 minutes daily. Follow up in 1 month.",
        "follow_up_date": "2025-02-01", "created_at": f"{today_str}T09:25:00", "file_url": None, "hospital_id": "h1",
    },
    {
        "id": "presc2", "appointment_id": "apt5", "patient_id": "u3", "doctor_id": "d3",
        "doctor_name": "Dr. Emily Rodriguez",
        "diagnosis": "Knee Osteoarthritis (Grade II)",
        "medicines": [
            {"name": "Diclofenac",  "dosage": "50mg", "frequency": "Twice daily", "duration": "14 days", "instructions": "After meals"},
            {"name": "Pantoprazole","dosage": "40mg",  "frequency": "Once daily",  "duration": "14 days", "instructions": "Before breakfast"},
        ],
        "notes": "Avoid climbing stairs. Use knee support. Physiotherapy recommended.",
        "follow_up_date": "2025-01-25", "created_at": f"{today_str}T08:40:00", "file_url": None, "hospital_id": "h1",
    },
    {
        "id": "presc3", "appointment_id": "apt6", "patient_id": "u2", "doctor_id": "d8",
        "doctor_name": "Dr. David Thompson",
        "diagnosis": "Annual health checkup — Normal",
        "medicines": [
            {"name": "Vitamin D3", "dosage": "60000 IU", "frequency": "Once weekly", "duration": "8 weeks", "instructions": "With milk"},
            {"name": "Omega-3",    "dosage": "1000mg",   "frequency": "Once daily",  "duration": "90 days", "instructions": "With meals"},
        ],
        "notes": "All vitals normal. Maintain healthy diet and exercise routine.",
        "follow_up_date": "2026-01-06", "created_at": f"{today_str}T08:20:00", "file_url": None, "hospital_id": "h1",
    },
    {
        "id": "presc4", "appointment_id": "apt8", "patient_id": "u5", "doctor_id": "d5",
        "doctor_name": "Dr. Priya Patel",
        "diagnosis": "Chronic Migraine with Aura",
        "medicines": [
            {"name": "Sumatriptan",  "dosage": "50mg",  "frequency": "As needed (max 2/day)", "duration": "30 days", "instructions": "Take at onset of migraine"},
            {"name": "Propranolol",  "dosage": "40mg",  "frequency": "Twice daily",           "duration": "60 days", "instructions": "Do not stop abruptly"},
        ],
        "notes": "Avoid triggers (bright lights, stress). Keep migraine diary. Follow up in 2 months.",
        "follow_up_date": "2026-06-11", "created_at": f"{today_str}T09:15:00", "file_url": None, "hospital_id": "h1",
    },
    {
        "id": "presc5", "appointment_id": "apt11", "patient_id": "u7", "doctor_id": "d4",
        "doctor_name": "Dr. James Wilson",
        "diagnosis": "Lumbar Disc Herniation (L4-L5)",
        "medicines": [
            {"name": "Ibuprofen",    "dosage": "400mg", "frequency": "Three times daily", "duration": "10 days", "instructions": "After meals"},
            {"name": "Cyclobenzaprine","dosage": "5mg", "frequency": "At bedtime",        "duration": "10 days", "instructions": "May cause drowsiness"},
        ],
        "notes": "Avoid lifting heavy weights. MRI scheduled. Physiotherapy 3x/week.",
        "follow_up_date": "2026-04-25", "created_at": f"{today_str}T09:10:00", "file_url": None, "hospital_id": "h1",
    },
]

# ── Lab Test Types ─────────────────────────────────────────────────────────────
lab_test_types_db = [
    {"id": "lt1",  "name": "Complete Blood Count (CBC)",  "description": "Measures red/white blood cells and platelets", "price": 350.00,  "turnaround_hours": 4,  "category": "Hematology",    "hospital_id": "h1"},
    {"id": "lt2",  "name": "Lipid Profile",               "description": "Cholesterol and triglyceride levels",          "price": 650.00,  "turnaround_hours": 6,  "category": "Biochemistry",  "hospital_id": "h1"},
    {"id": "lt3",  "name": "Blood Glucose (Fasting)",     "description": "Fasting blood sugar level",                    "price": 120.00,  "turnaround_hours": 2,  "category": "Biochemistry",  "hospital_id": "h1"},
    {"id": "lt4",  "name": "HbA1c",                       "description": "3-month average blood sugar",                  "price": 550.00,  "turnaround_hours": 8,  "category": "Biochemistry",  "hospital_id": "h1"},
    {"id": "lt5",  "name": "Thyroid Profile (T3/T4/TSH)", "description": "Complete thyroid function test",               "price": 950.00,  "turnaround_hours": 12, "category": "Endocrinology", "hospital_id": "h1"},
    {"id": "lt6",  "name": "Urine Routine Examination",   "description": "Complete urine analysis",                     "price": 200.00,  "turnaround_hours": 3,  "category": "Pathology",     "hospital_id": "h1"},
    {"id": "lt7",  "name": "Liver Function Test (LFT)",   "description": "Liver enzymes and bilirubin levels",           "price": 750.00,  "turnaround_hours": 6,  "category": "Biochemistry",  "hospital_id": "h1"},
    {"id": "lt8",  "name": "ECG (Electrocardiogram)",     "description": "Heart electrical activity recording",          "price": 400.00,  "turnaround_hours": 1,  "category": "Cardiology",    "hospital_id": "h1"},
    {"id": "lt9",  "name": "Chest X-Ray",                 "description": "Lung and chest imaging",                      "price": 600.00,  "turnaround_hours": 2,  "category": "Radiology",     "hospital_id": "h1"},
    {"id": "lt10", "name": "COVID-19 RT-PCR",             "description": "SARS-CoV-2 detection test",                   "price": 800.00,  "turnaround_hours": 24, "category": "Microbiology",  "hospital_id": "h1"},
]

# ── Lab Test Bookings ──────────────────────────────────────────────────────────
lab_bookings_db = [
    {"id": "lb1", "patient_id": "u2", "test_type_id": "lt1", "appointment_id": "apt1", "status": "report_ready",   "booked_at": f"{today_str}T09:30:00", "sample_collected_at": f"{today_str}T10:00:00", "payment_status": "paid",    "amount": 350.00, "notes": "Ordered by Dr. Sarah Johnson", "hospital_id": "h1"},
    {"id": "lb2", "patient_id": "u2", "test_type_id": "lt2", "appointment_id": "apt1", "status": "report_ready",   "booked_at": f"{today_str}T09:30:00", "sample_collected_at": f"{today_str}T10:00:00", "payment_status": "paid",    "amount": 650.00, "notes": "Fasting sample required",       "hospital_id": "h1"},
    {"id": "lb3", "patient_id": "u3", "test_type_id": "lt8", "appointment_id": "apt5", "status": "processing",     "booked_at": f"{today_str}T08:45:00", "sample_collected_at": f"{today_str}T09:00:00", "payment_status": "paid",    "amount": 400.00, "notes": "Pre-surgery ECG",               "hospital_id": "h1"},
    {"id": "lb4", "patient_id": "u2", "test_type_id": "lt5", "appointment_id": None,   "status": "sample_collected","booked_at":f"{today_str}T07:00:00", "sample_collected_at": f"{today_str}T07:30:00",  "payment_status": "paid",    "amount": 950.00, "notes": "",                              "hospital_id": "h1"},
    {"id": "lb5", "patient_id": "u4", "test_type_id": "lt3", "appointment_id": "apt7", "status": "booked",         "booked_at": f"{today_str}T08:20:00", "sample_collected_at": None,                    "payment_status": "pending", "amount": 120.00, "notes": "",                              "hospital_id": "h1"},
]

# ── Reports ────────────────────────────────────────────────────────────────────
reports_db = [
    {"id": "rep1", "patient_id": "u2", "lab_booking_id": "lb1", "test_type_id": "lt1", "title": "Complete Blood Count Report",   "findings": "Hemoglobin: 14.2 g/dL (Normal)\nWBC: 7,800 cells/mcL (Normal)\nPlatelets: 2.8 Lakh (Normal)",               "interpretation": "All parameters within normal range.",                            "status": "normal",   "file_url": "mock://reports/cbc_john.pdf",   "uploaded_by": "u1", "created_at": f"{today_str}T13:00:00", "hospital_id": "h1"},
    {"id": "rep2", "patient_id": "u2", "lab_booking_id": "lb2", "test_type_id": "lt2", "title": "Lipid Profile Report",          "findings": "Total Cholesterol: 218 mg/dL (High)\nLDL: 142 mg/dL (High)\nHDL: 48 mg/dL (Low-Normal)",                   "interpretation": "Borderline dyslipidemia. Lifestyle modification advised.",       "status": "abnormal", "file_url": "mock://reports/lipid_john.pdf", "uploaded_by": "u1", "created_at": f"{today_str}T14:00:00", "hospital_id": "h1"},
    {"id": "rep3", "patient_id": "u3", "lab_booking_id": "lb3", "test_type_id": "lt8", "title": "ECG Report",                   "findings": "Rhythm: Normal sinus rhythm\nHeart Rate: 72 bpm\nPR Interval: 162 ms",                                       "interpretation": "ECG within normal limits. No ischemic changes.",               "status": "normal",   "file_url": "mock://reports/ecg_jane.pdf",   "uploaded_by": "u1", "created_at": f"{today_str}T10:30:00", "hospital_id": "h1"},
]

# ── Notifications ──────────────────────────────────────────────────────────────
notifications_db = [
    {"id": "n1",  "user_id": "u2",  "type": "appointment",  "title": "Appointment Reminder",    "message": "You have an appointment with Dr. Sarah Johnson at 10:00 AM today.",    "read": False, "action_url": "/patient/appointments", "created_at": f"{today_str}T07:00:00"},
    {"id": "n2",  "user_id": "u2",  "type": "report",       "title": "Lab Report Ready",        "message": "Your CBC report is ready. Click to view.",                             "read": False, "action_url": "/patient/reports",      "created_at": f"{today_str}T13:05:00"},
    {"id": "n3",  "user_id": "u2",  "type": "report",       "title": "Lipid Profile Ready",     "message": "Your Lipid Profile report is ready. Please review with your doctor.",  "read": False, "action_url": "/patient/reports",      "created_at": f"{today_str}T14:05:00"},
    {"id": "n4",  "user_id": "u2",  "type": "payment",      "title": "Payment Confirmed",       "message": "Payment of ₹500 confirmed.",                                           "read": True,  "action_url": "/patient/payments",     "created_at": f"{today_str}T08:56:00"},
    {"id": "n5",  "user_id": "u2",  "type": "appointment",  "title": "Follow-up Due",           "message": "Time for your monthly follow-up with Dr. Sarah Johnson.",               "read": False, "action_url": "/patient/book",         "created_at": f"{today_str}T09:00:00"},
    {"id": "n6",  "user_id": "u3",  "type": "appointment",  "title": "Appointment in 1 hour",   "message": "Your appointment with Dr. Emily Rodriguez is in 1 hour.",               "read": False, "action_url": "/patient/appointments", "created_at": f"{today_str}T07:00:00"},
    {"id": "n7",  "user_id": "u3",  "type": "prescription", "title": "Prescription Available",  "message": "Dr. Emily Rodriguez has uploaded your prescription.",                   "read": True,  "action_url": "/patient/prescriptions","created_at": f"{today_str}T08:45:00"},
    {"id": "n8",  "user_id": "u4",  "type": "appointment",  "title": "Appointment Confirmed",   "message": "Your appointment with Dr. David Thompson is confirmed.",                 "read": True,  "action_url": "/patient/appointments", "created_at": f"{today_str}T07:30:00"},
    # Doctor notifications
    {"id": "n9",  "user_id": "du1", "type": "appointment",  "title": "New Patient Waiting",     "message": "Token #3 — Bob Wilson is waiting for consultation.",                    "read": False, "action_url": "/doctor/queue",         "created_at": f"{today_str}T09:38:00"},
    {"id": "n10", "user_id": "du1", "type": "general",      "title": "Queue Update",            "message": "2 patients remaining in today's queue.",                                "read": False, "action_url": "/doctor/queue",         "created_at": f"{today_str}T09:30:00"},
]

# ── Medicine Reminders ─────────────────────────────────────────────────────────
medicine_reminders_db = [
    {"id": "mr1", "patient_id": "u2", "medicine_name": "Amlodipine",  "dosage": "5mg",     "frequency": "Once daily",   "times": ["Morning (8:00 AM)"],                                  "start_date": today_str, "end_date": "2025-02-01", "instructions": "Take in the morning with water", "active": True,  "prescription_id": "presc1", "created_at": f"{today_str}T09:30:00"},
    {"id": "mr2", "patient_id": "u2", "medicine_name": "Losartan",    "dosage": "50mg",     "frequency": "Once daily",   "times": ["Afternoon (2:00 PM)"],                                "start_date": today_str, "end_date": "2025-02-01", "instructions": "Take with lunch",               "active": True,  "prescription_id": "presc1", "created_at": f"{today_str}T09:30:00"},
    {"id": "mr3", "patient_id": "u2", "medicine_name": "Vitamin D3",  "dosage": "60000 IU", "frequency": "Once weekly",  "times": ["Morning (8:00 AM)"],                                  "start_date": today_str, "end_date": "2025-03-01", "instructions": "Take with milk on Sundays",     "active": True,  "prescription_id": "presc3", "created_at": f"{today_str}T08:25:00"},
    {"id": "mr4", "patient_id": "u3", "medicine_name": "Diclofenac",  "dosage": "50mg",     "frequency": "Twice daily",  "times": ["Morning (8:00 AM)", "Night (10:00 PM)"],              "start_date": today_str, "end_date": "2025-01-25", "instructions": "After meals only",              "active": True,  "prescription_id": "presc2", "created_at": f"{today_str}T08:45:00"},
    {"id": "mr5", "patient_id": "u3", "medicine_name": "Pantoprazole","dosage": "40mg",     "frequency": "Once daily",   "times": ["Before breakfast"],                                   "start_date": today_str, "end_date": "2025-01-25", "instructions": "30 mins before breakfast",      "active": True,  "prescription_id": "presc2", "created_at": f"{today_str}T08:45:00"},
    {"id": "mr6", "patient_id": "u2", "medicine_name": "Omega-3",     "dosage": "1000mg",   "frequency": "Once daily",   "times": ["Afternoon (2:00 PM)"],                                "start_date": today_str, "end_date": "2025-04-06", "instructions": "With meals",                    "active": True,  "prescription_id": "presc3", "created_at": f"{today_str}T08:25:00"},
]

# ── Notification Log ───────────────────────────────────────────────────────────
notification_log_db = []

# ── ID Counters ────────────────────────────────────────────────────────────────
_counters = {
    "user": 10, "appointment": 8, "availability": 40, "specialization": 7, "doctor": 9,
    "payment": 6, "prescription": 4, "lab_booking": 6, "report": 4,
    "notification": 11, "medicine_reminder": 7, "lab_test_type": 11, "hospital": 3,
}
_prefixes = {
    "user": "u", "appointment": "apt", "availability": "av",
    "specialization": "s", "doctor": "d", "payment": "pay",
    "prescription": "presc", "lab_booking": "lb", "report": "rep",
    "notification": "n", "medicine_reminder": "mr", "lab_test_type": "lt",
    "hospital": "h",
}

def next_id(entity: str) -> str:
    _counters[entity] += 1
    return f"{_prefixes[entity]}{_counters[entity]}"
