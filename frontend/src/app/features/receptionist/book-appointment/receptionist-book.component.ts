import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../../core/services/api.service';
import { TimeSlot } from '../../../shared/models/models';

const FEES: Record<string, number> = { s1: 500, s2: 800, s3: 700, s4: 600, s5: 400, s6: 300 };

@Component({
  selector: 'app-receptionist-book',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatIconModule, MatButtonModule, MatProgressSpinnerModule, MatSnackBarModule],
  templateUrl: './receptionist-book.component.html',
  styleUrls: ['./receptionist-book.component.scss']
})
export class ReceptionistBookComponent implements OnInit {
  private api   = inject(ApiService);
  private snack = inject(MatSnackBar);

  step    = signal(0);   // 0=Patient, 1=Doctor, 2=Date/Time, 3=Payment, 4=Success
  loading = signal(false);

  // ── Dept context ──────────────────────────────────────────────────────────────
  department  = signal<any>(null);
  deptDoctors = signal<any[]>([]);

  // ── Patient step ─────────────────────────────────────────────────────────────
  patientSearch   = signal('');
  patientResults  = signal<any[]>([]);
  selectedPatient = signal<any | null>(null);
  newPatient = { name: '', phone: '', email: '', age: null as number | null, gender: '' };

  // ── Booking steps ─────────────────────────────────────────────────────────────
  slots          = signal<TimeSlot[]>([]);
  selectedDoctor = signal<any | null>(null);
  selectedDate   = signal('');
  selectedSlot   = signal('');
  notes          = signal('');
  paymentMethod  = signal<'cash' | 'upi' | 'online'>('cash');

  // ── Result ────────────────────────────────────────────────────────────────────
  bookingResult = signal<any | null>(null);

  minDate = new Date().toISOString().split('T')[0];
  fee     = computed(() => FEES[this.department()?.id ?? ''] ?? 300);

  readonly UPI_ID = 'nbvsindhu@okhdfc';

  patientDisplayName = computed(() =>
    this.selectedPatient()?.name || this.newPatient.name || 'Patient'
  );

  ngOnInit() {
    this.api.getReceptionistMe().subscribe(data => {
      this.department.set(data.department);
    });
    this.api.getReceptionistDoctors().subscribe(docs => {
      this.deptDoctors.set(docs);
    });
  }

  searchPatients() {
    const q = this.patientSearch().trim();
    if (!q) { this.patientResults.set([]); return; }
    this.api.getReceptionistPatients(q).subscribe(r => this.patientResults.set(r));
  }

  selectExistingPatient(p: any) {
    this.selectedPatient.set(p);
    this.step.set(1);
  }

  useNewPatient() {
    if (!this.newPatient.name.trim()) {
      this.snack.open('Please enter the patient name', '', { duration: 2000 });
      return;
    }
    this.selectedPatient.set(null);
    this.step.set(1);
  }

  selectDoctor(doc: any) {
    this.selectedDoctor.set(doc);
    this.selectedSlot.set('');
    this.step.set(2);
  }

  onDateChange(d: string) {
    this.selectedDate.set(d);
    this.selectedSlot.set('');
    if (!d) return;
    this.loading.set(true);
    this.api.getDoctorSlots(this.selectedDoctor()!.id, d).subscribe({
      next: slots => { this.slots.set(slots); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  selectSlot(t: string) { this.selectedSlot.set(t); }

  confirm() {
    this.loading.set(true);
    const payload: any = {
      doctor_id:     this.selectedDoctor()!.id,
      date:          this.selectedDate(),
      time_slot:     this.selectedSlot(),
      notes:         this.notes(),
      payment_method: this.paymentMethod(),
    };

    if (this.selectedPatient()) {
      payload.patient_id = this.selectedPatient().id;
    } else {
      payload.patient = {
        name:   this.newPatient.name,
        phone:  this.newPatient.phone  || null,
        email:  this.newPatient.email  || null,
        age:    this.newPatient.age,
        gender: this.newPatient.gender || null,
      };
    }

    this.api.receptionistBook(payload).subscribe({
      next: result => {
        this.loading.set(false);
        this.bookingResult.set(result);
        this.step.set(4);
      },
      error: err => {
        this.loading.set(false);
        this.snack.open(err.error?.detail || 'Booking failed', '', { duration: 3000 });
      }
    });
  }

  reset() {
    this.step.set(0);
    this.bookingResult.set(null);
    this.selectedPatient.set(null);
    this.patientSearch.set('');
    this.patientResults.set([]);
    this.selectedDoctor.set(null);
    this.selectedDate.set('');
    this.selectedSlot.set('');
    this.notes.set('');
    this.paymentMethod.set('cash');
    this.newPatient = { name: '', phone: '', email: '', age: null, gender: '' };
  }

  goBack() { if (this.step() > 0 && this.step() < 4) this.step.update(n => n - 1); }

  printToken() {
    const r = this.bookingResult();
    if (!r) return;
    const w = window.open('', '_blank', 'width=420,height=580');
    if (!w) return;
    w.document.write(`<!DOCTYPE html><html><head><title>Token Receipt</title>
    <style>
      * { margin:0; padding:0; box-sizing:border-box; }
      body { font-family: Arial, sans-serif; padding: 24px; text-align: center; }
      .hospital { font-size: 17px; font-weight: 800; color: #004d40; margin-bottom: 4px; }
      .dept { font-size: 12px; color: #00695c; font-weight: 600; margin-bottom: 16px; }
      .token-box { background: #e8f5e9; border: 2px solid #00695c; border-radius: 12px; padding: 16px; margin: 16px 0; }
      .token-label { font-size: 12px; color: #607d8b; text-transform: uppercase; letter-spacing: 1px; }
      .token-num { font-size: 56px; font-weight: 900; color: #00695c; line-height: 1.1; }
      hr { border: none; border-top: 1px solid #e0e0e0; margin: 12px 0; }
      .row { display: flex; justify-content: space-between; margin: 6px 0; font-size: 13px; padding: 0 4px; }
      .paid-badge { background: #e8f5e9; color: #2e7d32; padding: 5px 14px; border-radius: 20px; font-weight: 700; display: inline-block; margin-top: 12px; font-size: 13px; }
      .footer { font-size: 10px; color: #bdbdbd; margin-top: 14px; }
    </style></head><body>
    <div class="hospital">MediCare+ City General Hospital</div>
    <div class="dept">${this.department()?.name || ''} Department</div>
    <div class="token-box">
      <div class="token-label">Token Number</div>
      <div class="token-num">#${r.token_number}</div>
    </div>
    <hr>
    <div class="row"><span>Patient</span><strong>${r.patient?.name}</strong></div>
    <div class="row"><span>Doctor</span><strong>${r.appointment?.doctor?.name}</strong></div>
    <div class="row"><span>Date</span><strong>${r.appointment?.date}</strong></div>
    <div class="row"><span>Time</span><strong>${r.appointment?.time_slot}</strong></div>
    <hr>
    <div class="row"><span>Amount Paid</span><strong>₹${r.payment?.amount}</strong></div>
    <div class="row"><span>Method</span><strong>${(r.payment?.method || '').toUpperCase()}</strong></div>
    <div class="paid-badge">✓ PAYMENT CONFIRMED</div>
    <div class="footer"><br>Please arrive 10 minutes early. Token valid for today only.</div>
    </body></html>`);
    w.document.close();
    setTimeout(() => w.print(), 300);
  }
}
