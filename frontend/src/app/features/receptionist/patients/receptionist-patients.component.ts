import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-receptionist-patients',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, MatIconModule, MatButtonModule, MatProgressSpinnerModule, MatSnackBarModule],
  templateUrl: './receptionist-patients.component.html',
  styleUrls: ['./receptionist-patients.component.scss']
})
export class ReceptionistPatientsComponent implements OnInit {
  api     = inject(ApiService);
  snack   = inject(MatSnackBar);
  loading = signal(true);
  saving  = signal(false);
  patients = signal<any[]>([]);
  search  = signal('');

  editingPatient = signal<any | null>(null);
  editForm: any = {};

  ngOnInit() { this.load(); }

  load() {
    this.loading.set(true);
    this.api.getReceptionistPatients(this.search() || undefined).subscribe({
      next: p => { this.patients.set(p); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  openEdit(p: any) {
    this.editForm = {
      name:       p.name       || '',
      phone:      p.phone      || '',
      email:      p.email      || '',
      age:        p.age        ?? null,
      gender:     p.gender     || '',
      blood_group: p.blood_group || '',
      address:    p.address    || '',
    };
    this.editingPatient.set(p);
  }

  closeEdit() { this.editingPatient.set(null); }

  saveEdit() {
    const p = this.editingPatient();
    if (!p || !this.editForm.name?.trim()) {
      this.snack.open('Name is required', '', { duration: 2000 });
      return;
    }
    this.saving.set(true);
    this.api.updateReceptionistPatient(p.id, this.editForm).subscribe({
      next: updated => {
        this.patients.update(list => list.map(x => x.id === p.id ? { ...x, ...updated } : x));
        this.saving.set(false);
        this.editingPatient.set(null);
        this.snack.open('Patient updated', '', { duration: 2000 });
      },
      error: err => {
        this.saving.set(false);
        this.snack.open(err.error?.detail || 'Update failed', '', { duration: 3000 });
      }
    });
  }
}
