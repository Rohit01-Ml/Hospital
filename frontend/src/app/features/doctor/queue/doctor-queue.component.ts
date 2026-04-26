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
    const wsProto = location.protocol === 'https:' ? 'wss' : 'ws';
    this.ws = new WebSocket(`${wsProto}://${location.host}/ws/queue/${doctorId}`);
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
      next: (res: any) => {
        this.saving.set(false);
        this.snack.open('✓ Prescription issued & consultation complete', '', { duration: 3000, panelClass: 'snack-success' });
        this._printPrescription(res?.prescription, apt, payload);
        this.prescribeApt.set(null);
        this.loadQueue();
      },
      error: () => {
        this.saving.set(false);
        this.snack.open('Failed to issue prescription', '', { duration: 3000 });
      }
    });
  }

  _printPrescription(presc: any, apt: any, payload: any) {
    const win = window.open('', '_blank', 'width=800,height=600');
    if (!win) return;
    const meds = (payload.medicines || []).map((m: any) =>
      `<tr><td>${m.name}</td><td>${m.dosage}</td><td>${m.frequency}</td><td>${m.duration}</td><td>${m.instructions || '-'}</td></tr>`
    ).join('');
    win.document.write(`
      <html><head><title>Prescription</title>
      <style>
        body{font-family:Arial,sans-serif;padding:32px;color:#111}
        h2{color:#1565c0}h3{margin-top:24px}
        table{width:100%;border-collapse:collapse;margin-top:8px}
        th{background:#1565c0;color:white;padding:8px;text-align:left}
        td{padding:8px;border-bottom:1px solid #ddd}
        .row{display:flex;gap:32px;margin:8px 0}.label{font-weight:bold;color:#555}
        @media print{button{display:none}}
      </style></head><body>
      <h2>Prescription</h2>
      <div class="row">
        <span><span class="label">Patient:</span> ${apt.patient?.name || ''}</span>
        <span><span class="label">Patient ID:</span> ${apt.patient_id}</span>
        <span><span class="label">Token:</span> #${apt.token_number}</span>
        <span><span class="label">Date:</span> ${new Date().toLocaleDateString()}</span>
      </div>
      <div class="row"><span><span class="label">Diagnosis:</span> ${payload.diagnosis}</span></div>
      <h3>Medicines</h3>
      <table><thead><tr><th>Medicine</th><th>Dosage</th><th>Frequency</th><th>Duration</th><th>Instructions</th></tr></thead>
      <tbody>${meds}</tbody></table>
      ${payload.notes ? `<h3>Notes</h3><p>${payload.notes}</p>` : ''}
      ${payload.follow_up_date ? `<p><span class="label">Follow-up:</span> ${payload.follow_up_date}</p>` : ''}
      <br><button onclick="window.print()">Print</button>
      </body></html>
    `);
    win.document.close();
    win.focus();
    setTimeout(() => win.print(), 500);
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
