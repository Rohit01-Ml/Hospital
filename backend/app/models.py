"""SQLAlchemy ORM models for the Hospital Management System."""
import json
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text,
    ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


# ── Helpers ────────────────────────────────────────────────────────────────────

def _cols(obj) -> dict:
    """Convert ORM row to plain dict (column values only)."""
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


# ── Hospital ───────────────────────────────────────────────────────────────────

class Hospital(Base):
    __tablename__ = "hospitals"

    id           = Column(String(20),  primary_key=True)
    name         = Column(String(200), nullable=False)
    slug         = Column(String(100))
    subscription = Column(String(50))
    admin_email  = Column(String(200))
    phone        = Column(String(50),  nullable=True)
    address      = Column(String(500), nullable=True)
    logo_url     = Column(String(500), nullable=True)
    active       = Column(Boolean, default=True)
    created_at   = Column(String(50))
    plan_features = Column(Text, default="[]")  # JSON list
    monthly_fee  = Column(Float, nullable=True)

    def to_dict(self):
        d = _cols(self)
        try:
            d["plan_features"] = json.loads(d["plan_features"]) if d["plan_features"] else []
        except Exception:
            d["plan_features"] = []
        return d


# ── Specialization ─────────────────────────────────────────────────────────────

class Specialization(Base):
    __tablename__ = "specializations"

    id          = Column(String(20),  primary_key=True)
    name        = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    icon        = Column(String(100), nullable=True)
    hospital_id = Column(String(20),  ForeignKey("hospitals.id"), nullable=True)

    def to_dict(self):
        return _cols(self)


# ── Doctor ─────────────────────────────────────────────────────────────────────

class Doctor(Base):
    __tablename__ = "doctors"

    id                = Column(String(20),  primary_key=True)
    name              = Column(String(200), nullable=False)
    specialization_id = Column(String(20),  ForeignKey("specializations.id"))
    experience_years  = Column(Integer, default=0)
    qualification     = Column(String(200), nullable=True)
    phone             = Column(String(50),  nullable=True)
    email             = Column(String(200), nullable=True)
    bio               = Column(Text,        nullable=True)
    rating            = Column(Float, default=0.0)
    patients_treated  = Column(Integer, default=0)
    image_url         = Column(String(500), nullable=True)
    available         = Column(Boolean, default=True)
    hospital_id       = Column(String(20),  ForeignKey("hospitals.id"), nullable=True)

    def to_dict(self):
        return _cols(self)


# ── User ───────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id                = Column(String(50),  primary_key=True)
    name              = Column(String(200), nullable=False)
    email             = Column(String(200), unique=True, nullable=False)
    password_hash     = Column(String(500))
    role              = Column(String(30))  # admin | patient | doctor | receptionist
    hospital_id       = Column(String(20),  ForeignKey("hospitals.id"), nullable=True)
    doctor_id         = Column(String(20),  ForeignKey("doctors.id"),   nullable=True)
    specialization_id = Column(String(20),  ForeignKey("specializations.id"), nullable=True)
    phone             = Column(String(50),  nullable=True)
    age               = Column(Integer,     nullable=True)
    gender            = Column(String(20),  nullable=True)
    blood_group       = Column(String(10),  nullable=True)
    address           = Column(String(500), nullable=True)
    created_at        = Column(String(50))

    def to_dict(self):
        return _cols(self)

    def safe_dict(self):
        d = self.to_dict()
        d.pop("password_hash", None)
        return d


# ── Availability ───────────────────────────────────────────────────────────────

class Availability(Base):
    __tablename__ = "availability"

    id                    = Column(String(20), primary_key=True)
    doctor_id             = Column(String(20), ForeignKey("doctors.id"))
    day_of_week           = Column(Integer)
    start_time            = Column(String(10))
    end_time              = Column(String(10))
    slot_duration_minutes = Column(Integer)
    max_patients          = Column(Integer)

    def to_dict(self):
        return _cols(self)


# ── Appointment ────────────────────────────────────────────────────────────────

class Appointment(Base):
    __tablename__ = "appointments"

    id                = Column(String(50),  primary_key=True)
    patient_id        = Column(String(50),  ForeignKey("users.id"))
    doctor_id         = Column(String(20),  ForeignKey("doctors.id"))
    specialization_id = Column(String(20),  ForeignKey("specializations.id"))
    date              = Column(String(20))
    time_slot         = Column(String(10))
    token_number      = Column(Integer)
    status            = Column(String(30), default="waiting")
    notes             = Column(Text, default="")
    priority          = Column(Boolean, default=False)
    estimated_wait    = Column(Integer, default=0)
    hospital_id       = Column(String(20), ForeignKey("hospitals.id"), nullable=True)
    booked_by         = Column(String(50), nullable=True)
    booked_by_role    = Column(String(20), nullable=True)

    def to_dict(self):
        return _cols(self)


# ── Queue State ────────────────────────────────────────────────────────────────

class QueueState(Base):
    __tablename__ = "queue_states"

    id            = Column(String(50), primary_key=True)  # "doctor_id:date"
    doctor_id     = Column(String(20), ForeignKey("doctors.id"))
    date          = Column(String(20))
    current_token = Column(Integer, default=0)

    def to_dict(self):
        return _cols(self)


# ── Queue History ──────────────────────────────────────────────────────────────

class QueueHistory(Base):
    __tablename__ = "queue_history"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id            = Column(String(20), ForeignKey("doctors.id"))
    date                 = Column(String(20))
    time_slot            = Column(String(10))
    actual_wait_minutes  = Column(Integer)
    patients_ahead       = Column(Integer)

    def to_dict(self):
        return _cols(self)


# ── Slot Booking Count ─────────────────────────────────────────────────────────

class SlotBookingCount(Base):
    __tablename__ = "slot_booking_counts"

    id        = Column(String(100), primary_key=True)  # "doctor_id:date:time_slot"
    doctor_id = Column(String(20))
    date      = Column(String(20))
    time_slot = Column(String(10))
    count     = Column(Integer, default=0)

    def to_dict(self):
        return _cols(self)


# ── Payment ────────────────────────────────────────────────────────────────────

class Payment(Base):
    __tablename__ = "payments"

    id                  = Column(String(50),  primary_key=True)
    appointment_id      = Column(String(50),  ForeignKey("appointments.id"))
    patient_id          = Column(String(50),  ForeignKey("users.id"))
    amount              = Column(Float)
    currency            = Column(String(10), default="INR")
    status              = Column(String(20), default="pending")
    razorpay_order_id   = Column(String(100), nullable=True)
    razorpay_payment_id = Column(String(100), nullable=True)
    method              = Column(String(50),  nullable=True)
    created_at          = Column(String(50))
    hospital_id         = Column(String(20),  nullable=True)

    def to_dict(self):
        return _cols(self)


# ── Prescription + Medicines ───────────────────────────────────────────────────

class Prescription(Base):
    __tablename__ = "prescriptions"

    id             = Column(String(50),  primary_key=True)
    appointment_id = Column(String(50),  ForeignKey("appointments.id"), nullable=True)
    patient_id     = Column(String(50),  ForeignKey("users.id"))
    doctor_id      = Column(String(20),  ForeignKey("doctors.id"))
    doctor_name    = Column(String(200))
    diagnosis      = Column(Text)
    notes          = Column(Text, default="")
    follow_up_date = Column(String(20),  nullable=True)
    created_at     = Column(String(50))
    file_url       = Column(String(500), nullable=True)
    hospital_id    = Column(String(20),  nullable=True)

    medicines = relationship(
        "PrescriptionMedicine",
        back_populates="prescription",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def to_dict(self):
        d = _cols(self)
        d["medicines"] = [m.to_dict() for m in self.medicines]
        return d


class PrescriptionMedicine(Base):
    __tablename__ = "prescription_medicines"

    id              = Column(Integer,    primary_key=True, autoincrement=True)
    prescription_id = Column(String(50), ForeignKey("prescriptions.id"))
    name            = Column(String(200))
    dosage          = Column(String(100))
    frequency       = Column(String(100))
    duration        = Column(String(100))
    instructions    = Column(String(500), default="")

    prescription = relationship("Prescription", back_populates="medicines")

    def to_dict(self):
        return {
            "name": self.name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "duration": self.duration,
            "instructions": self.instructions,
        }


# ── Lab Test Type ──────────────────────────────────────────────────────────────

class LabTestType(Base):
    __tablename__ = "lab_test_types"

    id               = Column(String(20),  primary_key=True)
    name             = Column(String(200), nullable=False)
    description      = Column(String(500), nullable=True)
    price            = Column(Float)
    turnaround_hours = Column(Integer)
    category         = Column(String(100))
    hospital_id      = Column(String(20),  nullable=True)

    def to_dict(self):
        return _cols(self)


# ── Lab Booking ────────────────────────────────────────────────────────────────

class LabBooking(Base):
    __tablename__ = "lab_bookings"

    id                 = Column(String(50),  primary_key=True)
    patient_id         = Column(String(50),  ForeignKey("users.id"))
    test_type_id       = Column(String(20),  ForeignKey("lab_test_types.id"))
    appointment_id     = Column(String(50),  nullable=True)
    status             = Column(String(50),  default="booked")
    booked_at          = Column(String(50))
    sample_collected_at = Column(String(50), nullable=True)
    payment_status     = Column(String(20),  default="pending")
    amount             = Column(Float)
    notes              = Column(Text, default="")
    hospital_id        = Column(String(20),  nullable=True)

    def to_dict(self):
        return _cols(self)


# ── Report ─────────────────────────────────────────────────────────────────────

class Report(Base):
    __tablename__ = "reports"

    id              = Column(String(50),  primary_key=True)
    patient_id      = Column(String(50),  ForeignKey("users.id"))
    lab_booking_id  = Column(String(50),  nullable=True)
    test_type_id    = Column(String(20),  nullable=True)
    title           = Column(String(300))
    findings        = Column(Text)
    interpretation  = Column(Text, nullable=True)
    status          = Column(String(20))
    file_url        = Column(String(500), nullable=True)
    uploaded_by     = Column(String(50),  nullable=True)
    created_at      = Column(String(50))
    hospital_id     = Column(String(20),  nullable=True)

    def to_dict(self):
        return _cols(self)


# ── Notification ───────────────────────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    id         = Column(String(50),  primary_key=True)
    user_id    = Column(String(50),  ForeignKey("users.id"))
    type       = Column(String(50))
    title      = Column(String(300))
    message    = Column(Text)
    read       = Column(Boolean, default=False)
    action_url = Column(String(300), nullable=True)
    created_at = Column(String(50))

    def to_dict(self):
        return _cols(self)


# ── Medicine Reminder ──────────────────────────────────────────────────────────

class MedicineReminder(Base):
    __tablename__ = "medicine_reminders"

    id              = Column(String(50),  primary_key=True)
    patient_id      = Column(String(50),  ForeignKey("users.id"))
    medicine_name   = Column(String(200))
    dosage          = Column(String(100))
    frequency       = Column(String(100))
    times           = Column(Text, default="[]")  # JSON list
    start_date      = Column(String(20))
    end_date        = Column(String(20))
    instructions    = Column(Text, default="")
    active          = Column(Boolean, default=True)
    prescription_id = Column(String(50), nullable=True)
    created_at      = Column(String(50))

    def to_dict(self):
        d = _cols(self)
        try:
            d["times"] = json.loads(d["times"]) if d["times"] else []
        except Exception:
            d["times"] = []
        return d
