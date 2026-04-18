import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../../core/services/api.service';

interface Medicine { name: string; dosage: string; frequency: string; duration: string; instructions: string; }

@Component({
  selector: 'app-receptionist-patient-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatIconModule, MatProgressSpinnerModule, MatSnackBarModule],
  templateUrl: './receptionist-patient-detail.component.html',
  styleUrls: ['./receptionist-patient-detail.component.scss']
})
export class ReceptionistPatientDetailComponent implements OnInit {
  api    = inject(ApiService);
  route  = inject(ActivatedRoute);
  snack  = inject(MatSnackBar);

  loading = signal(true);
  saving  = signal(false);
  patient   = signal<any>(null);
  appointments = signal<any[]>([]);
  prescriptions = signal<any[]>([]);

  activeTab = signal<'info' | 'appointments' | 'prescriptions'>('info');

  // Edit patient
  editForm: any = {};
  editOpen = signal(false);

  // Add / Edit prescription
  prescModal = signal(false);
  editingPrescId = signal<string | null>(null);
  prescForm = {
    appointment_id: '' as string | null,
    diagnosis: '',
    notes: '',
    follow_up_date: '',
    medicines: [] as Medicine[],
  };

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id')!;
    this.load(id);
  }

  load(id: string) {
    this.loading.set(true);
    this.api.getReceptionistPatientDetail(id).subscribe({
      next: data => {
        this.patient.set(data.patient);
        this.appointments.set(data.appointments || []);
        this.prescriptions.set(data.prescriptions || []);
        this.loading.set(false);
      },
      error: () => { this.loading.set(false); this.snack.open('Failed to load patient', '', { duration: 3000 }); }
    });
  }

  // ── Edit patient info ─────────────────────────────────────────────────────
  openEdit() {
    const p = this.patient();
    this.editForm = { name: p.name || '', phone: p.phone || '', email: p.email || '',
      age: p.age ?? null, gender: p.gender || '', blood_group: p.blood_group || '', address: p.address || '' };
    this.editOpen.set(true);
  }

  saveEdit() {
    if (!this.editForm.name?.trim()) { this.snack.open('Name is required', '', { duration: 2000 }); return; }
    this.saving.set(true);
    this.api.updateReceptionistPatient(this.patient().id, this.editForm).subscribe({
      next: updated => { this.patient.set(updated); this.saving.set(false); this.editOpen.set(false); this.snack.open('Patient updated', '', { duration: 2000 }); },
      error: err => { this.saving.set(false); this.snack.open(err.error?.detail || 'Update failed', '', { duration: 3000 }); }
    });
  }

  // ── Prescriptions ─────────────────────────────────────────────────────────
  openAddPrescription(apt: any = null) {
    this.editingPrescId.set(null);
    this.prescForm = { appointment_id: apt?.id || null, diagnosis: '', notes: '', follow_up_date: '', medicines: [] };
    this.addMedicine();
    this.prescModal.set(true);
  }

  openEditPrescription(p: any) {
    this.editingPrescId.set(p.id);
    this.prescForm = {
      appointment_id: p.appointment_id || null,
      diagnosis: p.diagnosis || '',
      notes: p.notes || '',
      follow_up_date: p.follow_up_date || '',
      medicines: (p.medicines || []).map((m: any) => ({ ...m })),
    };
    this.prescModal.set(true);
  }

  addMedicine() {
    this.prescForm.medicines.push({ name: '', dosage: '', frequency: '', duration: '', instructions: '' });
  }

  removeMedicine(i: number) { this.prescForm.medicines.splice(i, 1); }

  savePrescription() {
    if (!this.prescForm.diagnosis.trim()) { this.snack.open('Diagnosis is required', '', { duration: 2000 }); return; }
    if (!this.prescForm.medicines.length || !this.prescForm.medicines[0].name.trim()) {
      this.snack.open('At least one medicine is required', '', { duration: 2000 }); return;
    }
    this.saving.set(true);
    const pid = this.patient().id;
    const editId = this.editingPrescId();

    const payload = {
      appointment_id: this.prescForm.appointment_id || undefined,
      diagnosis: this.prescForm.diagnosis,
      notes: this.prescForm.notes,
      follow_up_date: this.prescForm.follow_up_date || undefined,
      medicines: this.prescForm.medicines.filter(m => m.name.trim()),
    };

    const req$ = editId
      ? this.api.receptionistUpdatePrescription(editId, payload)
      : this.api.receptionistAddPrescription(pid, payload);

    req$.subscribe({
      next: () => {
        this.saving.set(false);
        this.prescModal.set(false);
        this.snack.open(editId ? 'Prescription updated' : 'Prescription added', '', { duration: 2500 });
        this.load(pid);
      },
      error: err => { this.saving.set(false); this.snack.open(err.error?.detail || 'Failed', '', { duration: 3000 }); }
    });
  }

  statusColor(s: string) {
    return { waiting: 'wait', in_progress: 'prog', completed: 'done', cancelled: 'cancel' }[s] ?? '';
  }

  genderIcon(g: string) { return g === 'female' ? 'female' : g === 'male' ? 'male' : 'person'; }
}
