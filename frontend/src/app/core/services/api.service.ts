import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Specialization, Doctor, Availability, TimeSlot, Appointment,
  QueueStatus, MyQueueStatus, Payment, Prescription, LabTestType,
  LabBooking, Report, Notification, MedicineReminder,
  Hospital, SymptomCheckResult, SmartQueueResult, SmartSlotsResult,
  AiInsights, DoctorQueueStatus,
} from '../../shared/models/models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly BASE = '/api';
  constructor(private http: HttpClient) {}

  // ── Specializations ──────────────────────────────────────────────────────────
  getSpecializations(): Observable<Specialization[]> { return this.http.get<Specialization[]>(`${this.BASE}/specializations/`); }
  createSpecialization(d: any): Observable<Specialization> { return this.http.post<Specialization>(`${this.BASE}/specializations/`, d); }
  updateSpecialization(id: string, d: any): Observable<Specialization> { return this.http.put<Specialization>(`${this.BASE}/specializations/${id}`, d); }
  deleteSpecialization(id: string): Observable<any> { return this.http.delete(`${this.BASE}/specializations/${id}`); }

  // ── Doctors ──────────────────────────────────────────────────────────────────
  getDoctors(specializationId?: string): Observable<Doctor[]> {
    let p = new HttpParams();
    if (specializationId) p = p.set('specialization_id', specializationId);
    return this.http.get<Doctor[]>(`${this.BASE}/doctors/`, { params: p });
  }
  getDoctor(id: string): Observable<Doctor> { return this.http.get<Doctor>(`${this.BASE}/doctors/${id}`); }
  createDoctor(d: any): Observable<Doctor> { return this.http.post<Doctor>(`${this.BASE}/doctors/`, d); }
  updateDoctor(id: string, d: any): Observable<Doctor> { return this.http.put<Doctor>(`${this.BASE}/doctors/${id}`, d); }
  deleteDoctor(id: string): Observable<any> { return this.http.delete(`${this.BASE}/doctors/${id}`); }
  getDoctorSlots(doctorId: string, date: string): Observable<TimeSlot[]> {
    return this.http.get<TimeSlot[]>(`${this.BASE}/doctors/${doctorId}/slots`, { params: new HttpParams().set('date_str', date) });
  }
  getDoctorAvailability(doctorId: string): Observable<Availability[]> { return this.http.get<Availability[]>(`${this.BASE}/doctors/${doctorId}/availability`); }
  createAvailability(d: any): Observable<Availability> { return this.http.post<Availability>(`${this.BASE}/doctors/availability`, d); }
  deleteAvailability(id: string): Observable<any> { return this.http.delete(`${this.BASE}/doctors/availability/${id}`); }

  // ── Appointments ─────────────────────────────────────────────────────────────
  getAppointments(): Observable<Appointment[]> { return this.http.get<Appointment[]>(`${this.BASE}/appointments/`); }
  getTodayAppointments(): Observable<Appointment[]> { return this.http.get<Appointment[]>(`${this.BASE}/appointments/today`); }
  bookAppointment(d: any): Observable<Appointment> { return this.http.post<Appointment>(`${this.BASE}/appointments/`, d); }
  cancelAppointment(id: string): Observable<any> { return this.http.delete(`${this.BASE}/appointments/${id}`); }
  updateAppointment(id: string, d: any): Observable<Appointment> { return this.http.put<Appointment>(`${this.BASE}/appointments/${id}`, d); }

  // ── Queue ────────────────────────────────────────────────────────────────────
  getQueue(doctorId: string, date?: string): Observable<QueueStatus> {
    let p = new HttpParams();
    if (date) p = p.set('date_str', date);
    return this.http.get<QueueStatus>(`${this.BASE}/queue/${doctorId}`, { params: p });
  }
  getMyQueueStatus(doctorId: string, date?: string): Observable<MyQueueStatus> {
    let p = new HttpParams();
    if (date) p = p.set('date_str', date);
    return this.http.get<MyQueueStatus>(`${this.BASE}/queue/${doctorId}/my-status`, { params: p });
  }
  nextPatient(doctorId: string): Observable<any>  { return this.http.post(`${this.BASE}/queue/${doctorId}/next`, {}); }
  skipPatient(doctorId: string, aptId: string): Observable<any> { return this.http.post(`${this.BASE}/queue/${doctorId}/skip/${aptId}`, {}); }
  completeAppointment(doctorId: string, aptId: string): Observable<any> { return this.http.post(`${this.BASE}/queue/${doctorId}/complete/${aptId}`, {}); }

  // ── Payments ─────────────────────────────────────────────────────────────────
  getPayments(): Observable<Payment[]> { return this.http.get<Payment[]>(`${this.BASE}/payments/`); }
  getPaymentByAppointment(aptId: string): Observable<Payment> { return this.http.get<Payment>(`${this.BASE}/payments/appointment/${aptId}`); }
  initiatePayment(d: any): Observable<any> { return this.http.post(`${this.BASE}/payments/initiate`, d); }
  verifyPayment(d: any): Observable<any>  { return this.http.post(`${this.BASE}/payments/verify`, d); }
  mockPay(aptId: string): Observable<any> { return this.http.post(`${this.BASE}/payments/mock-pay/${aptId}`, {}); }

  // ── Prescriptions ────────────────────────────────────────────────────────────
  getPrescriptions(): Observable<Prescription[]> { return this.http.get<Prescription[]>(`${this.BASE}/prescriptions/`); }
  getPrescription(id: string): Observable<Prescription> { return this.http.get<Prescription>(`${this.BASE}/prescriptions/${id}`); }
  createPrescription(d: any): Observable<Prescription> { return this.http.post<Prescription>(`${this.BASE}/prescriptions/`, d); }
  updatePrescription(id: string, d: any): Observable<Prescription> { return this.http.put<Prescription>(`${this.BASE}/prescriptions/${id}`, d); }
  downloadPrescription(id: string): Observable<any> { return this.http.get(`${this.BASE}/prescriptions/${id}/download`); }

  // ── Lab Tests ────────────────────────────────────────────────────────────────
  getLabTestTypes(): Observable<LabTestType[]> { return this.http.get<LabTestType[]>(`${this.BASE}/lab-tests/types`); }
  createLabTestType(d: any): Observable<LabTestType> { return this.http.post<LabTestType>(`${this.BASE}/lab-tests/types`, d); }
  updateLabTestType(id: string, d: any): Observable<LabTestType> { return this.http.put<LabTestType>(`${this.BASE}/lab-tests/types/${id}`, d); }
  deleteLabTestType(id: string): Observable<any> { return this.http.delete(`${this.BASE}/lab-tests/types/${id}`); }
  getLabBookings(): Observable<LabBooking[]> { return this.http.get<LabBooking[]>(`${this.BASE}/lab-tests/bookings`); }
  bookLabTest(d: any): Observable<LabBooking> { return this.http.post<LabBooking>(`${this.BASE}/lab-tests/bookings`, d); }
  updateLabBookingStatus(id: string, d: any): Observable<LabBooking> { return this.http.put<LabBooking>(`${this.BASE}/lab-tests/bookings/${id}`, d); }
  cancelLabBooking(id: string): Observable<any> { return this.http.delete(`${this.BASE}/lab-tests/bookings/${id}`); }

  // ── Reports ──────────────────────────────────────────────────────────────────
  getReports(): Observable<Report[]> { return this.http.get<Report[]>(`${this.BASE}/reports/`); }
  getReport(id: string): Observable<Report> { return this.http.get<Report>(`${this.BASE}/reports/${id}`); }
  uploadReport(d: any): Observable<Report> { return this.http.post<Report>(`${this.BASE}/reports/`, d); }
  updateReport(id: string, d: any): Observable<Report> { return this.http.put<Report>(`${this.BASE}/reports/${id}`, d); }
  deleteReport(id: string): Observable<any> { return this.http.delete(`${this.BASE}/reports/${id}`); }
  downloadReport(id: string): Observable<any> { return this.http.get(`${this.BASE}/reports/${id}/download`); }

  // ── Notifications ─────────────────────────────────────────────────────────────
  getNotifications(): Observable<Notification[]> { return this.http.get<Notification[]>(`${this.BASE}/notifications/`); }
  getUnreadCount(): Observable<{count: number}> { return this.http.get<{count: number}>(`${this.BASE}/notifications/unread-count`); }
  markNotificationRead(id: string): Observable<any> { return this.http.put(`${this.BASE}/notifications/${id}/read`, {}); }
  markAllRead(): Observable<any> { return this.http.put(`${this.BASE}/notifications/read-all`, {}); }
  createNotification(d: any): Observable<Notification> { return this.http.post<Notification>(`${this.BASE}/notifications/`, d); }
  broadcastNotification(d: any): Observable<any> { return this.http.post(`${this.BASE}/notifications/broadcast`, d); }

  // ── Medicine Reminders ────────────────────────────────────────────────────────
  getMedicineReminders(): Observable<MedicineReminder[]> { return this.http.get<MedicineReminder[]>(`${this.BASE}/medicine-reminders/`); }
  getActiveReminders(): Observable<MedicineReminder[]> { return this.http.get<MedicineReminder[]>(`${this.BASE}/medicine-reminders/active`); }
  createReminder(d: any): Observable<MedicineReminder> { return this.http.post<MedicineReminder>(`${this.BASE}/medicine-reminders/`, d); }
  updateReminder(id: string, d: any): Observable<MedicineReminder> { return this.http.put<MedicineReminder>(`${this.BASE}/medicine-reminders/${id}`, d); }
  deleteReminder(id: string): Observable<any> { return this.http.delete(`${this.BASE}/medicine-reminders/${id}`); }

  // ── Hospitals (SaaS Tenants) ──────────────────────────────────────────────────
  getHospitals(): Observable<Hospital[]> { return this.http.get<Hospital[]>(`${this.BASE}/hospitals/`); }
  getHospital(id: string): Observable<Hospital> { return this.http.get<Hospital>(`${this.BASE}/hospitals/${id}`); }
  createHospital(d: any): Observable<Hospital> { return this.http.post<Hospital>(`${this.BASE}/hospitals/`, d); }
  updateHospital(id: string, d: any): Observable<Hospital> { return this.http.put<Hospital>(`${this.BASE}/hospitals/${id}`, d); }
  getPlans(): Observable<any> { return this.http.get(`${this.BASE}/hospitals/plans`); }

  // ── AI Features ───────────────────────────────────────────────────────────────
  checkSymptoms(symptoms: string, age?: number, gender?: string): Observable<SymptomCheckResult> {
    return this.http.post<SymptomCheckResult>(`${this.BASE}/ai/symptom-check`, { symptoms, age, gender });
  }
  getSmartQueue(doctorId: string, date?: string): Observable<SmartQueueResult> {
    return this.http.post<SmartQueueResult>(`${this.BASE}/ai/smart-queue`, { doctor_id: doctorId, date });
  }
  getSmartSlots(doctorId: string, date: string): Observable<SmartSlotsResult> {
    return this.http.post<SmartSlotsResult>(`${this.BASE}/ai/smart-slots`, { doctor_id: doctorId, date });
  }
  getAiInsights(): Observable<AiInsights> { return this.http.get<AiInsights>(`${this.BASE}/ai/insights`); }

  // ── Doctor Portal ─────────────────────────────────────────────────────────────
  getDoctorMe(): Observable<any> { return this.http.get(`${this.BASE}/doctor/me`); }
  getDoctorAppointments(): Observable<Appointment[]> { return this.http.get<Appointment[]>(`${this.BASE}/doctor/appointments`); }
  getDoctorTodayAppointments(): Observable<Appointment[]> { return this.http.get<Appointment[]>(`${this.BASE}/doctor/appointments/today`); }
  getDoctorAppointmentsRange(): Observable<Appointment[]> { return this.http.get<Appointment[]>(`${this.BASE}/doctor/appointments/range`); }
  getDoctorQueue(): Observable<DoctorQueueStatus> { return this.http.get<DoctorQueueStatus>(`${this.BASE}/doctor/queue`); }
  startPatient(aptId: string): Observable<any> { return this.http.post(`${this.BASE}/doctor/appointments/${aptId}/start`, {}); }
  completePatient(aptId: string): Observable<any> { return this.http.post(`${this.BASE}/doctor/appointments/${aptId}/complete`, {}); }
  skipPatientDoctor(aptId: string): Observable<any> { return this.http.post(`${this.BASE}/doctor/appointments/${aptId}/skip`, {}); }
  updateAptNotes(aptId: string, notes: string): Observable<any> { return this.http.put(`${this.BASE}/doctor/appointments/${aptId}/notes`, { notes }); }
  getDoctorPrescriptions(): Observable<Prescription[]> { return this.http.get<Prescription[]>(`${this.BASE}/doctor/prescriptions`); }
  writePrescription(d: any): Observable<Prescription> { return this.http.post<Prescription>(`${this.BASE}/doctor/prescriptions`, d); }
  prescribeAndComplete(aptId: string, d: any): Observable<any> { return this.http.post(`${this.BASE}/doctor/appointments/${aptId}/prescribe-complete`, d); }
  getDoctorPatients(): Observable<any[]> { return this.http.get<any[]>(`${this.BASE}/doctor/patients`); }

  // ── Receptionist ──────────────────────────────────────────────────────────────
  getReceptionistMe(): Observable<any>            { return this.http.get(`${this.BASE}/receptionist/me`); }
  getReceptionistDashboard(): Observable<any>     { return this.http.get(`${this.BASE}/receptionist/dashboard`); }
  getReceptionistPatients(search?: string): Observable<any[]> {
    let p = new HttpParams();
    if (search) p = p.set('search', search);
    return this.http.get<any[]>(`${this.BASE}/receptionist/patients`, { params: p });
  }
  updateReceptionistPatient(patientId: string, d: any): Observable<any> { return this.http.put(`${this.BASE}/receptionist/patients/${patientId}`, d); }
  registerWalkInPatient(d: any): Observable<any>  { return this.http.post(`${this.BASE}/receptionist/register-patient`, d); }
  receptionistBook(d: any): Observable<any>       { return this.http.post(`${this.BASE}/receptionist/book`, d); }
  getQueueOverview(): Observable<any[]>            { return this.http.get<any[]>(`${this.BASE}/receptionist/queue-overview`); }
  getTodayAllAppointments(): Observable<any[]>     { return this.http.get<any[]>(`${this.BASE}/receptionist/appointments/today`); }
  getReceptionistDoctors(): Observable<any[]>      { return this.http.get<any[]>(`${this.BASE}/receptionist/doctors`); }
  getReceptionistDoctorQueue(doctorId: string): Observable<any> { return this.http.get(`${this.BASE}/receptionist/queue/${doctorId}`); }
  receptionistNextPatient(doctorId: string): Observable<any>    { return this.http.post(`${this.BASE}/receptionist/queue/${doctorId}/next`, {}); }
  receptionistUpdateAptStatus(aptId: string, status: string): Observable<any> { return this.http.post(`${this.BASE}/receptionist/appointments/${aptId}/status`, { status }); }
  receptionistTogglePriority(aptId: string): Observable<any>    { return this.http.post(`${this.BASE}/receptionist/appointments/${aptId}/priority`, {}); }
  getReceptionistAllPrescriptions(search?: string): Observable<any[]> {
    let p = new HttpParams();
    if (search) p = p.set('search', search);
    return this.http.get<any[]>(`${this.BASE}/receptionist/prescriptions`, { params: p });
  }
  getReceptionistPatientDetail(patientId: string): Observable<any> { return this.http.get(`${this.BASE}/receptionist/patients/${patientId}`); }
  getReceptionistPatientPrescriptions(patientId: string): Observable<any[]> { return this.http.get<any[]>(`${this.BASE}/receptionist/patients/${patientId}/prescriptions`); }
  receptionistAddPrescription(patientId: string, d: any): Observable<any> { return this.http.post(`${this.BASE}/receptionist/patients/${patientId}/prescriptions`, d); }
  receptionistUpdatePrescription(prescriptionId: string, d: any): Observable<any> { return this.http.put(`${this.BASE}/receptionist/prescriptions/${prescriptionId}`, d); }
}
