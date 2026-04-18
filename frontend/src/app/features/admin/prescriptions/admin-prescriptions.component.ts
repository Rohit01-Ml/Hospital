import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators, FormArray } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
import { ApiService } from '../../../core/services/api.service';
import { Prescription } from '../../../shared/models/models';

@Component({
  selector: 'app-admin-prescriptions',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule,
    MatCardModule, MatButtonModule, MatIconModule,
    MatFormFieldModule, MatInputModule, MatTableModule,
    MatProgressSpinnerModule, MatExpansionModule, MatTooltipModule, MatDividerModule],
  templateUrl: './admin-prescriptions.component.html',
  styleUrls: ['./admin-prescriptions.component.scss']
})
export class AdminPrescriptionsComponent implements OnInit {
  api = inject(ApiService);
  fb = inject(FormBuilder);
  prescriptions = signal<Prescription[]>([]);
  loading = signal(true);
  saving = signal(false);
  showForm = signal(false);

  form = this.fb.group({
    appointment_id: ['', Validators.required],
    patient_id: ['', Validators.required],
    doctor_id: ['', Validators.required],
    doctor_name: ['', Validators.required],
    diagnosis: ['', Validators.required],
    notes: [''],
    follow_up_date: [''],
    medicines: this.fb.array([])
  });

  get medicines() { return this.form.get('medicines') as FormArray; }

  ngOnInit() { this.load(); this.addMedicine(); }

  load() {
    this.loading.set(true);
    this.api.getPrescriptions().subscribe({
      next: d => { this.prescriptions.set(d); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  addMedicine() {
    this.medicines.push(this.fb.group({
      name: ['', Validators.required],
      dosage: [''],
      frequency: [''],
      duration: [''],
      instructions: ['']
    }));
  }

  removeMedicine(i: number) { this.medicines.removeAt(i); }

  openAdd() { this.form.reset(); this.medicines.clear(); this.addMedicine(); this.showForm.set(true); }

  save() {
    if (this.form.invalid) return;
    this.saving.set(true);
    this.api.createPrescription(this.form.value).subscribe({
      next: () => { this.saving.set(false); this.showForm.set(false); this.load(); },
      error: () => this.saving.set(false)
    });
  }

  download(id: string) {
    this.api.downloadPrescription(id).subscribe(r => alert(r.message || 'Download initiated'));
  }

  cancel() { this.showForm.set(false); }
}
