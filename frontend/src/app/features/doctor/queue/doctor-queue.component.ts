import { Component, OnInit, OnDestroy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormArray, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';
import { DoctorQueueStatus, Appointment } from '../../../shared/models/models';

@Component({
  selector: 'app-doctor-queue',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, MatCardModule, MatButtonModule,
    MatIconModule, MatProgressSpinnerModule, MatTooltipModule,
    MatFormFieldModule, MatInputModule, MatSnackBarModule],
  templateUrl: './doctor-queue.component.html',
  styleUrls: ['./doctor-queue.component.scss']
})
export class DoctorQueueComponent implements OnInit, OnDestroy {
  api   = inject(ApiService);
  auth  = inject(AuthService);
  fb    = inject(FormBuilder);
  snack = inject(MatSnackBar);

  loading    = signal(true);
  saving     = signal(false);
  queue      = signal<DoctorQueueStatus | null>(null);
  wsStatus   = signal<'connecting' | 'connected' | 'disconnected'>('connecting');
  /** The appointment currently open in the prescription panel */
  prescribeApt = signal<Appointment | null>(null);

  private ws?: WebSocket;
  private reconnectTimer?: any;

  rxForm = this.fb.group({
    diagnosis:     ['', Validators.required],
    notes:         [''],
    follow_up_date:[''],
    medicines: this.fb.array([this.newMed()])
  });

  get medicines() { return this.rxForm.get('medicines') as FormArray; }

  newMed() {
    return this.fb.group({
      name:         ['', Validators.required],
      dosage:       [''],
      frequency:    [''],
      duration:     [''],
      instructions: ['']
    });
  }

  addMedicine()           { this.medicines.push(this.newMed()); }
  removeMedicine(i: number) { if (this.medicines.length > 1) this.medicines.removeAt(i); }

  ngOnInit() {
    this.loadQueue();
    this.connectWS();
  }

  loadQueue() {
    this.api.getDoctorQueue().subscribe({
      next: q => { this.queue.set(q); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  connectWS() {
    const doctorId = this.auth.user()?.doctor_id;
    if (!doctorId) return;
    this.wsStatus.set('connecting');
    this.ws = new WebSocket(`ws://localhost:8000/ws/queue/${doctorId}`);
    this.ws.onopen    = () => this.wsStatus.set('connected');
    this.ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === 'queue_update') {
          this.queue.update(q => q ? { ...q, ...data } : data);
        }
      } catch {}
    };
    this.ws.onclose = () => {
      this.wsStatus.set('disconnected');
      this.reconnectTimer = setTimeout(() => this.connectWS(), 4000);
    };
    this.ws.onerror = () => this.wsStatus.set('disconnected');
  }

  start(apt: Appointment) {
    this.api.startPatient(apt.id).subscribe(() => {
      this.loadQueue();
      // Automatically open prescription form for this patient
      setTimeout(() => {
        const updated = this.queue()?.appointments.find(a => a.id === apt.id);
        this.openPrescribe(updated || apt);
      }, 300);
    });
  }

  openPrescribe(apt: Appointment) {
    this.prescribeApt.set(apt);
    this.rxForm.reset();
    // Clear medicines and add one fresh row
    while (this.medicines.length > 0) this.medicines.removeAt(0);
    this.medicines.push(this.newMed());
  }

  closePrescribe() { this.prescribeApt.set(null); }

  submitPrescription() {
    if (this.rxForm.invalid) return;
    const apt = this.prescribeApt();
    if (!apt) return;
    this.saving.set(true);

    const payload = {
      appointment_id: apt.id,
      patient_id:     apt.patient_id,
      diagnosis:      this.rxForm.value.diagnosis,
      notes:          this.rxForm.value.notes || '',
      follow_up_date: this.rxForm.value.follow_up_date || null,
      medicines:      this.rxForm.value.medicines
    };

    this.api.prescribeAndComplete(apt.id, payload).subscribe({
      next: () => {
        this.saving.set(false);
        this.prescribeApt.set(null);
        this.snack.open('✓ Prescription issued & consultation complete', '', { duration: 3000, panelClass: 'snack-success' });
        this.loadQueue();
      },
      error: () => {
        this.saving.set(false);
        this.snack.open('Failed to issue prescription', '', { duration: 3000 });
      }
    });
  }

  skip(apt: Appointment) {
    this.api.skipPatientDoctor(apt.id).subscribe(() => {
      this.loadQueue();
      if (this.prescribeApt()?.id === apt.id) this.closePrescribe();
    });
  }

  get progressPct() {
    const q = this.queue();
    if (!q || !q.total_patients) return 0;
    return Math.round(((q.completed || 0) / q.total_patients) * 100);
  }

  statusColor(s: string) {
    const m: any = { waiting: '#ff9800', in_progress: '#1565c0', completed: '#4caf50', cancelled: '#9e9e9e', skipped: '#bdbdbd' };
    return m[s] || '#9e9e9e';
  }

  ngOnDestroy() {
    clearTimeout(this.reconnectTimer);
    this.ws?.close();
  }
}
