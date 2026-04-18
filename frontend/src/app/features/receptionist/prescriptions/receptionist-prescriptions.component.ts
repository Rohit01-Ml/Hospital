import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../../core/services/api.service';

interface Medicine { name: string; dosage: string; frequency: string; duration: string; instructions: string; }

@Component({
  selector: 'app-receptionist-prescriptions',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatIconModule, MatProgressSpinnerModule, MatSnackBarModule],
  templateUrl: './receptionist-prescriptions.component.html',
  styleUrls: ['./receptionist-prescriptions.component.scss']
})
export class ReceptionistPrescriptionsComponent implements OnInit {
  api   = inject(ApiService);
  snack = inject(MatSnackBar);

  loading       = signal(true);
  saving        = signal(false);
  prescriptions = signal<any[]>([]);
  patients      = signal<any[]>([]);
  search        = signal('');

  // Modal state
  modal         = signal(false);
  editingId     = signal<string | null>(null);
  selectedPatient = signal<any | null>(null);
  patientSearch = signal('');
  patientResults = signal<any[]>([]);

  prescForm = {
    patient_id: '',
    appointment_id: null as string | null,
    diagnosis: '',
    notes: '',
    follow_up_date: '',
    medicines: [] as Medicine[],
  };

  // Follow-up days helper
  followUpDays = signal<number | null>(null);

  setFollowUpDays(days: number | null) {
    this.followUpDays.set(days);
    if (days && days > 0) {
      const d = new Date();
      d.setDate(d.getDate() + days);
      this.prescForm.follow_up_date = d.toISOString().split('T')[0];
    } else {
      this.prescForm.follow_up_date = '';
    }
  }

  formatFollowUp(iso: string): string {
    if (!iso) return '';
    return new Date(iso + 'T00:00:00').toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
  }

  // View detail
  viewing = signal<any | null>(null);

  ngOnInit() { this.load(); }

  load() {
    this.loading.set(true);
    this.api.getReceptionistAllPrescriptions(this.search() || undefined).subscribe({
      next: p => { this.prescriptions.set(p); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  searchPrescriptions() { this.load(); }

  // Patient search for new prescription
  searchPatients() {
    const q = this.patientSearch().trim();
    if (!q) { this.patientResults.set([]); return; }
    this.api.getReceptionistPatients(q).subscribe(r => this.patientResults.set(r));
  }

  selectPatient(p: any) {
    this.selectedPatient.set(p);
    this.prescForm.patient_id = p.id;
    this.patientSearch.set(p.name);
    this.patientResults.set([]);
  }

  openAdd() {
    this.editingId.set(null);
    this.selectedPatient.set(null);
    this.patientSearch.set('');
    this.patientResults.set([]);
    this.followUpDays.set(null);
    this.prescForm = { patient_id: '', appointment_id: null, diagnosis: '', notes: '', follow_up_date: '', medicines: [] };
    this.addMedicine();
    this.modal.set(true);
  }

  openEdit(p: any) {
    this.editingId.set(p.id);
    this.selectedPatient.set(p.patient);
    this.patientSearch.set(p.patient?.name || '');
    this.prescForm = {
      patient_id: p.patient_id,
      appointment_id: p.appointment_id || null,
      diagnosis: p.diagnosis || '',
      notes: p.notes || '',
      follow_up_date: p.follow_up_date || '',
      medicines: (p.medicines || []).map((m: any) => ({ ...m })),
    };
    this.modal.set(true);
  }

  closeModal() { this.modal.set(false); }

  addMedicine() {
    this.prescForm.medicines.push({ name: '', dosage: '', frequency: '', duration: '', instructions: '' });
  }

  removeMedicine(i: number) {
    if (this.prescForm.medicines.length > 1) this.prescForm.medicines.splice(i, 1);
  }

  save() {
    if (!this.prescForm.patient_id) { this.snack.open('Select a patient', '', { duration: 2000 }); return; }
    if (!this.prescForm.diagnosis.trim()) { this.snack.open('Enter diagnosis', '', { duration: 2000 }); return; }
    if (!this.prescForm.medicines[0]?.name.trim()) { this.snack.open('Add at least one medicine', '', { duration: 2000 }); return; }

    this.saving.set(true);
    const payload = {
      appointment_id: this.prescForm.appointment_id || undefined,
      diagnosis: this.prescForm.diagnosis,
      notes: this.prescForm.notes,
      follow_up_date: this.prescForm.follow_up_date || undefined,
      medicines: this.prescForm.medicines.filter(m => m.name.trim()),
    };

    const editId = this.editingId();
    const req$ = editId
      ? this.api.receptionistUpdatePrescription(editId, payload)
      : this.api.receptionistAddPrescription(this.prescForm.patient_id, payload);

    req$.subscribe({
      next: () => {
        this.saving.set(false);
        this.modal.set(false);
        this.snack.open(editId ? 'Prescription updated' : 'Prescription added', '', { duration: 2500 });
        this.load();
      },
      error: err => {
        this.saving.set(false);
        this.snack.open(err.error?.detail || 'Failed to save', '', { duration: 3000 });
      }
    });
  }

  viewDetail(p: any) { this.viewing.set(p); }
  closeView() { this.viewing.set(null); }
}
