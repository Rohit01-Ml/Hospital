import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatStepperModule } from '@angular/material/stepper';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';
import { Specialization, Doctor, TimeSlot } from '../../../shared/models/models';

// Consultation fee map (mirrors backend CONSULTATION_FEES)
const CONSULTATION_FEES: Record<string, number> = {
  s1: 500, s2: 800, s3: 700, s4: 600, s5: 400, s6: 300
};

@Component({
  selector: 'app-book-appointment',
  standalone: true,
  imports: [
    CommonModule, RouterLink, FormsModule,
    MatStepperModule, MatButtonModule, MatIconModule, MatCardModule,
    MatFormFieldModule, MatInputModule, MatProgressSpinnerModule, MatSnackBarModule
  ],
  templateUrl: './book-appointment.component.html',
  styleUrls: ['./book-appointment.component.scss']
})
export class BookAppointmentComponent implements OnInit {
  private api   = inject(ApiService);
  private auth  = inject(AuthService);
  private snack = inject(MatSnackBar);
  private router = inject(Router);

  step = signal(0);
  loading = signal(false);
  payStatus = signal<'idle' | 'booking' | 'paying' | 'verifying'>('idle');

  specializations = signal<Specialization[]>([]);
  doctors         = signal<Doctor[]>([]);
  slots           = signal<TimeSlot[]>([]);

  selectedSpec   = signal<Specialization | null>(null);
  selectedDoctor = signal<Doctor | null>(null);
  selectedDate   = signal<string>('');
  selectedSlot   = signal<string>('');
  notes          = signal<string>('');

  fee = computed(() => {
    const spec = this.selectedSpec();
    return spec ? (CONSULTATION_FEES[spec.id] ?? 300) : 0;
  });

  minDate = new Date().toISOString().split('T')[0];

  ngOnInit() {
    this.api.getSpecializations().subscribe(s => this.specializations.set(s));
  }

  selectSpec(spec: Specialization) {
    this.selectedSpec.set(spec);
    this.selectedDoctor.set(null);
    this.selectedSlot.set('');
    this.loading.set(true);
    this.api.getDoctors(spec.id).subscribe(docs => {
      this.doctors.set(docs.filter(d => d.available));
      this.loading.set(false);
      this.step.set(1);
    });
  }

  selectDoctor(doc: Doctor) {
    this.selectedDoctor.set(doc);
    this.selectedSlot.set('');
    this.step.set(2);
  }

  onDateChange(date: string) {
    this.selectedDate.set(date);
    this.selectedSlot.set('');
    if (!date) return;
    this.loading.set(true);
    this.api.getDoctorSlots(this.selectedDoctor()!.id, date).subscribe({
      next: slots => { this.slots.set(slots); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  selectSlot(t: string) { this.selectedSlot.set(t); }

  /** Step 1: book appointment → Step 2: initiate payment → Step 3: Razorpay modal */
  confirm() {
    const doc  = this.selectedDoctor()!;
    const spec = this.selectedSpec()!;
    this.loading.set(true);
    this.payStatus.set('booking');

    this.api.bookAppointment({
      doctor_id: doc.id,
      specialization_id: spec.id,
      date: this.selectedDate(),
      time_slot: this.selectedSlot(),
      notes: this.notes()
    }).subscribe({
      next: apt => {
        this.payStatus.set('paying');
        // Initiate Razorpay order
        this.api.initiatePayment({ appointment_id: apt.id, amount: this.fee(), currency: 'INR' }).subscribe({
          next: order => this.openRazorpay(order, apt),
          error: () => {
            // Appointment booked but payment init failed — still navigate
            this.loading.set(false);
            this.payStatus.set('idle');
            this.snack.open(`Appointment booked! Token #${apt.token_number}. Pay later from My Appointments.`, '', { duration: 5000 });
            this.router.navigate(['/patient/appointments']);
          }
        });
      },
      error: err => {
        this.loading.set(false);
        this.payStatus.set('idle');
        this.snack.open(err.error?.detail || 'Booking failed', '', { duration: 3000, panelClass: 'snack-error' });
      }
    });
  }

  private openRazorpay(order: any, apt: any) {
    const user = this.auth.user();
    const options = {
      key: order.razorpay_key,
      amount: order.amount * 100,      // paise
      currency: 'INR',
      name: 'MediCare+ Hospital',
      description: `Consultation — ${this.selectedSpec()?.name}`,
      image: '',
      order_id: order.razorpay_order_id,
      handler: (response: any) => {
        this.payStatus.set('verifying');
        this.api.verifyPayment({
          razorpay_order_id:  response.razorpay_order_id,
          razorpay_payment_id: response.razorpay_payment_id,
          razorpay_signature:  response.razorpay_signature ?? 'mock_signature',
        }).subscribe({
          next: () => {
            this.loading.set(false);
            this.payStatus.set('idle');
            this.snack.open(
              `Payment successful! Token #${apt.token_number}`,
              '', { duration: 4000, panelClass: 'snack-success' }
            );
            this.router.navigate(['/patient/appointments']);
          },
          error: () => {
            this.loading.set(false);
            this.payStatus.set('idle');
            this.snack.open('Payment done but verification failed. Contact support.', '', { duration: 5000 });
            this.router.navigate(['/patient/appointments']);
          }
        });
      },
      modal: {
        ondismiss: () => {
          this.loading.set(false);
          this.payStatus.set('idle');
          this.snack.open(
            `Appointment saved (Token #${apt.token_number}). Complete payment from My Appointments.`,
            'OK', { duration: 6000 }
          );
          this.router.navigate(['/patient/appointments']);
        }
      },
      prefill: {
        name:    user?.name ?? '',
        email:   user?.email ?? '',
        contact: '',
      },
      notes: { appointment_id: apt.id },
      theme: { color: '#1a237e' }
    };

    const rzp = new (window as any).Razorpay(options);
    rzp.on('payment.failed', (resp: any) => {
      this.loading.set(false);
      this.payStatus.set('idle');
      this.snack.open(`Payment failed: ${resp.error?.description || 'Unknown error'}`, '', { duration: 5000 });
    });
    rzp.open();
  }

  goBack() { if (this.step() > 0) this.step.update(n => n - 1); }
}
