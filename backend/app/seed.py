"""Seed the database from mock_data.py — run once to populate initial data.

Usage:
    cd backend
    python -m app.seed
"""
import json
from datetime import datetime

# Load .env before importing database so DATABASE_URL is set
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.database import SessionLocal, engine
from app import models
from app.mock_data import (
    hospitals_db, users_db, specializations_db, doctors_db, availability_db,
    appointments_db, queue_state_db, queue_history_db, slot_booking_counts_db,
    payments_db, prescriptions_db, lab_test_types_db, lab_bookings_db,
    reports_db, notifications_db, medicine_reminders_db,
)


def seed():
    # Create all tables
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Skip if already seeded
        if db.query(models.Hospital).count() > 0:
            print("Database already seeded. Skipping.")
            return

        print("Seeding hospitals...")
        for h in hospitals_db:
            d = dict(h)
            d["plan_features"] = json.dumps(d.get("plan_features", []))
            db.add(models.Hospital(**d))
        db.commit()

        print("Seeding specializations...")
        for s in specializations_db:
            db.add(models.Specialization(**s))
        db.commit()

        print("Seeding doctors...")
        for doc in doctors_db:
            db.add(models.Doctor(**doc))
        db.commit()

        print("Seeding users...")
        for u in users_db:
            db.add(models.User(**u))
        db.commit()

        print("Seeding availability...")
        for a in availability_db:
            db.add(models.Availability(**a))
        db.commit()

        print("Seeding appointments...")
        for a in appointments_db:
            apt = dict(a)
            apt.setdefault("priority", False)
            apt.setdefault("booked_by", None)
            apt.setdefault("booked_by_role", None)
            db.add(models.Appointment(**apt))
        db.commit()

        print("Seeding queue states...")
        for key, qs in queue_state_db.items():
            db.add(models.QueueState(id=key, **qs))
        db.commit()

        print("Seeding queue history...")
        for qh in queue_history_db:
            db.add(models.QueueHistory(**qh))
        db.commit()

        print("Seeding slot booking counts...")
        for key, count in slot_booking_counts_db.items():
            parts = key.split(":")
            time_slot = ":".join(parts[2:])
            db.add(models.SlotBookingCount(
                id=key, doctor_id=parts[0], date=parts[1],
                time_slot=time_slot, count=count,
            ))
        db.commit()

        print("Seeding payments...")
        for p in payments_db:
            db.add(models.Payment(**p))
        db.commit()

        print("Seeding prescriptions...")
        for presc in prescriptions_db:
            presc_data = dict(presc)
            medicines = presc_data.pop("medicines", [])
            db.add(models.Prescription(**presc_data))
            db.flush()
            for med in medicines:
                db.add(models.PrescriptionMedicine(
                    prescription_id=presc_data["id"], **med))
        db.commit()

        print("Seeding lab test types...")
        for lt in lab_test_types_db:
            db.add(models.LabTestType(**lt))
        db.commit()

        print("Seeding lab bookings...")
        for lb in lab_bookings_db:
            db.add(models.LabBooking(**lb))
        db.commit()

        print("Seeding reports...")
        for r in reports_db:
            db.add(models.Report(**r))
        db.commit()

        print("Seeding notifications...")
        for n in notifications_db:
            db.add(models.Notification(**n))
        db.commit()

        print("Seeding medicine reminders...")
        for mr in medicine_reminders_db:
            mr_data = dict(mr)
            mr_data["times"] = json.dumps(mr_data.get("times", []))
            db.add(models.MedicineReminder(**mr_data))
        db.commit()

        print("Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
