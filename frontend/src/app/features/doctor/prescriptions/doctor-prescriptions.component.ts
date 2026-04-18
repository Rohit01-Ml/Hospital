import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators, FormArray } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ApiService } from '../../../core/services/api.service';
import { Prescription, Appointment } from '../../../shared/models/models';

@Component({
  selector: 'app-doctor-prescriptions',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule,
    MatIconModule, MatButtonModule, MatFormFieldModule,
    MatInputModule, MatSelectModule, MatProgressSpinnerModule, MatTooltipModule],
  templateUrl: './doctor-prescriptions.component.html',
  styleUrls: ['./doctor-prescriptions.component.scss']
})
export class DoctorPrescriptionsComponent implements OnInit {
  api = inject(ApiService);
  fb  = inject(FormBuilder);

  prescriptions = signal<Prescription[]>([]);
  appointments  = signal<Appointment[]>([]);
  loading   = signal(true);
  saving    = signal(false);
  showForm  = signal(false);
  followUpDays = signal<number | null>(null);
  followUpDate = signal('');

  form = this.fb.group({
    appointment_id: ['', Validators.required],
    patient_id:     ['', Validators.required],
    diagnosis:      ['', Validators.required],
    notes:          [''],
    follow_up_date: [''],
    medicines: this.fb.array([])
  });

  get medicines() { return this.form.get('medicines') as FormArray; }

  ngOnInit() { this.load(); this.addMedicine(); }

  load() {
    this.loading.set(true);
    Promise.all([
      new Promise<void>(r => this.api.getDoctorPrescriptions().subscribe(d => { this.prescriptions.set(d); r(); })),
      new Promise<void>(r => this.api.getDoctorTodayAppointments().subscribe(d => { this.appointments.set(d); r(); })),
    ]).then(() => this.loading.set(false));
  }

  openNew() {
    this.form.reset(); this.medicines.clear(); this.addMedicine();
    this.followUpDays.set(null); this.followUpDate.set('');
    this.showForm.set(true);
  }

  addMedicine() {
    this.medicines.push(this.fb.group({
      name: ['', Validators.required], dosage: [''],
      frequency: [''], duration: [''], instructions: ['']
    }));
  }

  removeMedicine(i: number) { if (this.medicines.length > 1) this.medicines.removeAt(i); }

  fillFromAppointment(aptId: string) {
    const apt = this.appointments().find(a => a.id === aptId);
    if (apt) this.form.patchValue({ patient_id: apt.patient_id });
  }

  setFollowUpDays(days: number | null) {
    this.followUpDays.set(days);
    if (days && days > 0) {
      const d = new Date();
      d.setDate(d.getDate() + days);
      const iso = d.toISOString().split('T')[0];
      this.followUpDate.set(iso);
      this.form.patchValue({ follow_up_date: iso });
    } else {
      this.followUpDate.set('');
      this.form.patchValue({ follow_up_date: '' });
    }
  }

  formatFollowUpDisplay(iso: string): string {
    if (!iso) return '';
    return new Date(iso + 'T00:00:00').toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
  }

  save() {
    if (this.form.invalid) return;
    this.saving.set(true);
    this.api.writePrescription(this.form.value).subscribe({
      next: () => { this.saving.set(false); this.showForm.set(false); this.load(); },
      error: () => this.saving.set(false)
    });
  }

  cancel() { this.showForm.set(false); }
}
