import { Routes } from '@angular/router';
import { authGuard, adminGuard, patientGuard, publicGuard, doctorGuard, receptionistGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', loadComponent: () => import('./features/landing/landing.component').then(m => m.LandingComponent) },
  { path: 'login',    canActivate: [publicGuard], loadComponent: () => import('./features/auth/login/login.component').then(m => m.LoginComponent) },
  { path: 'register', canActivate: [publicGuard], loadComponent: () => import('./features/auth/register/register.component').then(m => m.RegisterComponent) },

  // ── Patient ──────────────────────────────────────────────────────────────────
  {
    path: 'patient', canActivate: [authGuard, patientGuard],
    loadComponent: () => import('./features/patient/patient-layout/patient-layout.component').then(m => m.PatientLayoutComponent),
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard',          loadComponent: () => import('./features/patient/dashboard/dashboard.component').then(m => m.DashboardComponent) },
      { path: 'book',               loadComponent: () => import('./features/patient/book-appointment/book-appointment.component').then(m => m.BookAppointmentComponent) },
      { path: 'appointments',       loadComponent: () => import('./features/patient/my-appointments/my-appointments.component').then(m => m.MyAppointmentsComponent) },
      { path: 'queue/:doctorId',    loadComponent: () => import('./features/patient/queue-status/queue-status.component').then(m => m.QueueStatusComponent) },
      { path: 'prescriptions',      loadComponent: () => import('./features/patient/prescriptions/prescriptions.component').then(m => m.PrescriptionsComponent) },
      { path: 'lab-tests',          loadComponent: () => import('./features/patient/lab-tests/lab-tests.component').then(m => m.LabTestsComponent) },
      { path: 'reports',            loadComponent: () => import('./features/patient/reports/reports.component').then(m => m.ReportsComponent) },
      { path: 'notifications',      loadComponent: () => import('./features/patient/notifications/notifications.component').then(m => m.NotificationsComponent) },
      { path: 'medicine-reminders', loadComponent: () => import('./features/patient/medicine-reminders/medicine-reminders.component').then(m => m.MedicineRemindersComponent) },
      { path: 'payments',           loadComponent: () => import('./features/patient/payments/payments.component').then(m => m.PaymentsComponent) },
      { path: 'symptom-checker',    loadComponent: () => import('./features/patient/symptom-checker/symptom-checker.component').then(m => m.SymptomCheckerComponent) },
    ]
  },

  // ── Admin ─────────────────────────────────────────────────────────────────────
  {
    path: 'admin', canActivate: [authGuard, adminGuard],
    loadComponent: () => import('./features/admin/admin-layout/admin-layout.component').then(m => m.AdminLayoutComponent),
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard',       loadComponent: () => import('./features/admin/dashboard/admin-dashboard.component').then(m => m.AdminDashboardComponent) },
      { path: 'doctors',         loadComponent: () => import('./features/admin/doctors/doctors.component').then(m => m.DoctorsComponent) },
      { path: 'specializations', loadComponent: () => import('./features/admin/specializations/specializations.component').then(m => m.SpecializationsComponent) },
      { path: 'queue',           loadComponent: () => import('./features/admin/queue/queue.component').then(m => m.QueueComponent) },
      { path: 'lab-tests',       loadComponent: () => import('./features/admin/lab-tests/admin-lab-tests.component').then(m => m.AdminLabTestsComponent) },
      { path: 'reports',         loadComponent: () => import('./features/admin/reports/admin-reports.component').then(m => m.AdminReportsComponent) },
      { path: 'prescriptions',   loadComponent: () => import('./features/admin/prescriptions/admin-prescriptions.component').then(m => m.AdminPrescriptionsComponent) },
      { path: 'notifications',   loadComponent: () => import('./features/admin/notifications/admin-notifications.component').then(m => m.AdminNotificationsComponent) },
      { path: 'hospitals',       loadComponent: () => import('./features/admin/hospitals/hospitals.component').then(m => m.HospitalsComponent) },
    ]
  },

  // ── Doctor Portal ─────────────────────────────────────────────────────────────
  {
    path: 'doctor', canActivate: [authGuard, doctorGuard],
    loadComponent: () => import('./features/doctor/doctor-layout/doctor-layout.component').then(m => m.DoctorLayoutComponent),
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard',     loadComponent: () => import('./features/doctor/dashboard/doctor-dashboard.component').then(m => m.DoctorDashboardComponent) },
      { path: 'appointments',  loadComponent: () => import('./features/doctor/appointments/doctor-appointments.component').then(m => m.DoctorAppointmentsComponent) },
      { path: 'queue',         loadComponent: () => import('./features/doctor/queue/doctor-queue.component').then(m => m.DoctorQueueComponent) },
      { path: 'prescriptions', loadComponent: () => import('./features/doctor/prescriptions/doctor-prescriptions.component').then(m => m.DoctorPrescriptionsComponent) },
      { path: 'patients',      loadComponent: () => import('./features/doctor/patients/doctor-patients.component').then(m => m.DoctorPatientsComponent) },
    ]
  },

  // ── Receptionist ─────────────────────────────────────────────────────────────
  {
    path: 'receptionist', canActivate: [authGuard, receptionistGuard],
    loadComponent: () => import('./features/receptionist/receptionist-layout/receptionist-layout.component').then(m => m.ReceptionistLayoutComponent),
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', loadComponent: () => import('./features/receptionist/dashboard/receptionist-dashboard.component').then(m => m.ReceptionistDashboardComponent) },
      { path: 'book',      loadComponent: () => import('./features/receptionist/book-appointment/receptionist-book.component').then(m => m.ReceptionistBookComponent) },
      { path: 'patients',  loadComponent: () => import('./features/receptionist/patients/receptionist-patients.component').then(m => m.ReceptionistPatientsComponent) },
      { path: 'queue',          loadComponent: () => import('./features/receptionist/queue-overview/queue-overview.component').then(m => m.QueueOverviewComponent) },
      { path: 'patients/:id',    loadComponent: () => import('./features/receptionist/patient-detail/receptionist-patient-detail.component').then(m => m.ReceptionistPatientDetailComponent) },
      { path: 'prescriptions',   loadComponent: () => import('./features/receptionist/prescriptions/receptionist-prescriptions.component').then(m => m.ReceptionistPrescriptionsComponent) },
    ]
  },

  { path: '**', redirectTo: '' }
];
