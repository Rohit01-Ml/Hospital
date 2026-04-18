"""
WhatsApp notification service using CallMeBot API (free).

Setup (one-time, per phone number):
  1. Save +34 644 59 84 61 in your WhatsApp contacts as "CallMeBot"
  2. Send this exact message to that number:
       I allow callmebot to send me messages
  3. You will receive your personal apikey in reply.
  4. Set it in .env:  CALLMEBOT_APIKEY=your_key_here

API docs: https://www.callmebot.com/blog/free-api-whatsapp-messages/
"""

import os
import urllib.request
import urllib.parse
import logging

logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
CALLMEBOT_APIKEY = os.getenv("CALLMEBOT_APIKEY", "")
HOSPITAL_PHONE   = os.getenv("HOSPITAL_PHONE", "+917075886985")
HOSPITAL_UPI     = os.getenv("HOSPITAL_UPI", "nbvsindhu@okhdfc")
HOSPITAL_NAME    = "MediCare+ City General Hospital"


def _send_whatsapp(phone: str, message: str) -> bool:
    """
    Send a WhatsApp message via CallMeBot.
    phone must include country code, e.g. +917989971159
    Returns True on success.
    """
    if not CALLMEBOT_APIKEY:
        logger.warning("[WhatsApp] CALLMEBOT_APIKEY not set — message not sent. "
                       "Follow setup in whatsapp_service.py to activate.")
        print(f"[WhatsApp MOCK] → {phone}: {message}")
        return False

    try:
        encoded_msg = urllib.parse.quote(message)
        url = (
            f"https://api.callmebot.com/whatsapp.php"
            f"?phone={phone}&text={encoded_msg}&apikey={CALLMEBOT_APIKEY}"
        )
        with urllib.request.urlopen(url, timeout=10) as resp:
            body = resp.read().decode()
            if resp.status == 200 and "Message Sent" in body:
                logger.info(f"[WhatsApp] ✓ Sent to {phone}")
                return True
            else:
                logger.warning(f"[WhatsApp] Unexpected response ({resp.status}): {body[:100]}")
                return False
    except Exception as e:
        logger.error(f"[WhatsApp] Failed to send to {phone}: {e}")
        return False


# ── Message Templates ──────────────────────────────────────────────────────────

def wa_appointment_booked(phone: str, patient_name: str, doctor_name: str,
                           date: str, time_slot: str, token: int, fee: float):
    msg = (
        f"✅ *Appointment Confirmed!*\n\n"
        f"🏥 *{HOSPITAL_NAME}*\n"
        f"👤 Patient: {patient_name}\n"
        f"👨‍⚕️ Doctor: {doctor_name}\n"
        f"📅 Date: {date}\n"
        f"🕐 Time: {time_slot}\n"
        f"🎫 Token: #{token}\n"
        f"💰 Fee: ₹{fee:.0f}\n\n"
        f"📲 Pay via UPI: *{HOSPITAL_UPI}*\n"
        f"📞 Helpline: {HOSPITAL_PHONE}\n\n"
        f"Please arrive 10 minutes early. Thank you!"
    )
    return _send_whatsapp(phone, msg)


def wa_appointment_reminder(phone: str, patient_name: str, doctor_name: str,
                             time_slot: str, token: int):
    msg = (
        f"⏰ *Appointment Reminder*\n\n"
        f"🏥 {HOSPITAL_NAME}\n"
        f"Hi {patient_name}! Your appointment is *TODAY*.\n\n"
        f"👨‍⚕️ Doctor: {doctor_name}\n"
        f"🕐 Time: {time_slot}\n"
        f"🎫 Token: #{token}\n\n"
        f"Please be on time. Carry your previous reports if any.\n"
        f"📞 {HOSPITAL_PHONE}"
    )
    return _send_whatsapp(phone, msg)


def wa_your_turn(phone: str, patient_name: str, doctor_name: str, token: int):
    msg = (
        f"🔔 *Your Turn is Coming!*\n\n"
        f"Hi {patient_name}, you are *NEXT* in the queue.\n"
        f"👨‍⚕️ Doctor: {doctor_name}\n"
        f"🎫 Token: #{token}\n\n"
        f"Please proceed to the consultation room.\n"
        f"🏥 {HOSPITAL_NAME}"
    )
    return _send_whatsapp(phone, msg)


def wa_prescription_ready(phone: str, patient_name: str, doctor_name: str,
                           diagnosis: str, follow_up: str = None):
    msg = (
        f"💊 *Prescription Ready*\n\n"
        f"Hi {patient_name}!\n"
        f"Dr. {doctor_name} has issued your prescription.\n\n"
        f"🩺 Diagnosis: {diagnosis}\n"
    )
    if follow_up:
        msg += f"📅 Follow-up: {follow_up}\n"
    msg += (
        f"\nView & download your prescription from the MediCare+ app.\n"
        f"📞 {HOSPITAL_PHONE}\n"
        f"🏥 {HOSPITAL_NAME}"
    )
    return _send_whatsapp(phone, msg)


def wa_payment_success(phone: str, patient_name: str, amount: float,
                        doctor_name: str, date: str):
    msg = (
        f"✅ *Payment Confirmed*\n\n"
        f"Hi {patient_name}!\n"
        f"Payment of *₹{amount:.0f}* received successfully.\n\n"
        f"👨‍⚕️ Doctor: {doctor_name}\n"
        f"📅 Date: {date}\n"
        f"🏥 {HOSPITAL_NAME}\n\n"
        f"Thank you for choosing us! Stay healthy. 🌿"
    )
    return _send_whatsapp(phone, msg)


def wa_medicine_reminder(phone: str, patient_name: str, medicine: str,
                          dosage: str, time: str):
    msg = (
        f"💊 *Medicine Reminder*\n\n"
        f"Hi {patient_name}! Time to take your medicine.\n\n"
        f"🔹 Medicine: *{medicine}*\n"
        f"🔹 Dosage: {dosage}\n"
        f"🕐 Time: {time}\n\n"
        f"Take care and get well soon! 🌟\n"
        f"🏥 {HOSPITAL_NAME}"
    )
    return _send_whatsapp(phone, msg)
