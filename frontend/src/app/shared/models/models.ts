export interface User {
  id: string; name: string; email: string;
  role: 'admin' | 'patient' | 'doctor' | 'receptionist'; created_at: string;
  doctor_id?: string; hospital_id?: string;
}
export interface AuthResponse {
  access_token: string; token_type: string; user: User;
}
export interface Hospital {
  id: string; name: string; subdomain: string;
  plan: 'starter' | 'professional' | 'enterprise';
  email: string; phone: string; address: string;
  active_since: string | null; created_at?: string;
  features?: { ai_features?: boolean; websocket?: boolean; whatsapp?: boolean; custom_domain?: boolean; [key: string]: any };
}
export interface Specialization {
  id: string; name: string; description: string; icon: string;
}
export interface Doctor {
  id: string; name: string; specialization_id: string;
  specialization?: Specialization; experience_years: number;
  qualification: string; phone: string; email: string;
  bio: string; rating: number; patients_treated: number;
  image_url: string | null; available: boolean; hospital_id?: string;
}
export interface Availability {
  id: string; doctor_id: string; day_of_week: number;
  start_time: string; end_time: string;
  slot_duration_minutes: number; max_patients: number;
}
export interface TimeSlot {
  time: string; available: boolean; availability_id: string;
}
export interface SmartSlot extends TimeSlot {
  booked_count: number; max_patients: number;
  load_percentage: number; crowd_level: 'low' | 'medium' | 'high';
  recommended: boolean;
}
export interface Appointment {
  id: string; patient_id: string; doctor_id: string;
  specialization_id: string; doctor?: Doctor; patient?: User;
  specialization?: Specialization; date: string;
  time_slot: string; token_number: number;
  status: 'waiting' | 'in_progress' | 'completed' | 'cancelled' | 'skipped';
  notes: string; estimated_wait?: number; hospital_id?: string;
  estimated_wait_minutes: number; avg_consult_minutes: number;
  patients_ahead: number;
}
export interface QueueStatus {
  doctor_id: string; date: string; current_token: number;
  total_patients: number; appointments: Appointment[];
  waiting?: number; in_progress?: number; completed?: number;
}
export interface MyQueueStatus {
  my_token: number; current_token: number;
  patients_ahead: number; status: string; appointment: Appointment;
  estimated_wait_minutes: number; avg_consult_minutes: number;
}
export interface DoctorQueueStatus {
  doctor_id: string; date: string; current_token: number;
  total_patients: number; waiting: number; in_progress: number;
  completed: number; appointments: Appointment[];
}

// ── Stage 2 ───────────────────────────────────────────────────────────────────
export interface Payment {
  id: string; appointment_id: string; patient_id: string;
  amount: number; currency: string;
  status: 'pending' | 'paid' | 'failed' | 'refunded';
  razorpay_order_id: string; razorpay_payment_id: string | null;
  method: string | null; created_at: string;
}
export interface MedicineItem {
  name: string; dosage: string; frequency: string;
  duration: string; instructions: string;
}
export interface Prescription {
  id: string; appointment_id: string; patient_id: string;
  doctor_id: string; doctor_name: string; doctor?: Doctor;
  diagnosis: string; medicines: MedicineItem[];
  notes: string; follow_up_date: string | null;
  file_url: string | null; created_at: string;
}
export interface LabTestType {
  id: string; name: string; description: string;
  price: number; turnaround_hours: number; category: string;
}
export interface LabBooking {
  id: string; patient_id: string; test_type_id: string;
  appointment_id: string | null; status: string;
  booked_at: string; sample_collected_at: string | null;
  payment_status: string; amount: number; notes: string;
  test_type?: LabTestType; patient_name?: string;
}
export interface Report {
  id: string; patient_id: string; lab_booking_id: string | null;
  test_type_id: string | null; title: string; findings: string;
  interpretation: string; status: 'normal' | 'abnormal' | 'critical';
  file_url: string | null; uploaded_by: string; created_at: string;
  test_type?: LabTestType; patient_name?: string;
}
export interface Notification {
  id: string; user_id: string; type: string;
  title: string; message: string; read: boolean;
  action_url: string | null; created_at: string;
}
export interface MedicineReminder {
  id: string; patient_id: string; medicine_name: string;
  dosage: string; frequency: string; times: string[];
  start_date: string; end_date: string | null;
  instructions: string; active: boolean;
  prescription_id: string | null; created_at: string;
}

// ── Stage 3 — AI ──────────────────────────────────────────────────────────────
export interface SymptomSuggestion {
  specialization: string; specialization_id: string; icon: string;
  confidence: number; confidence_pct: string;
  available_doctors: number; reason: string;
  matched_keywords: string[];
}
export interface SymptomCheckResult {
  query: string; suggestions: SymptomSuggestion[];
  top_recommendation: SymptomSuggestion | null; disclaimer: string;
}
export interface SmartQueueResult {
  doctor_id: string; doctor_name: string; date: string;
  current_token: number; patients_ahead: number;
  predicted_minutes: number; confidence: string;
  human_readable: string; method: string;
}
export interface SmartSlotsResult {
  doctor_id: string; doctor_name: string; date: string;
  slots: SmartSlot[]; best_slot: string | null;
}
export interface AiInsights {
  date: string; total_appointments: number;
  completed: number; waiting: number; throughput_pct: number;
  peak_hour: string;
  doctor_efficiency: Array<{doctor: string; total: number; completed: number; efficiency_pct: number}>;
  recommendation: string;
}
