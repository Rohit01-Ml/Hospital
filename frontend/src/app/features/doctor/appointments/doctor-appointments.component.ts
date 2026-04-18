import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';
import { Appointment } from '../../../shared/models/models';

@Component({
  selector: 'app-doctor-appointments',
  standalone: true,
  imports: [CommonModule, FormsModule, MatCardModule, MatButtonModule, MatIconModule,
    MatChipsModule, MatProgressSpinnerModule, MatTabsModule, MatFormFieldModule, MatInputModule],
  templateUrl: './doctor-appointments.component.html',
  styleUrls: ['./doctor-appointments.component.scss']
})
export class DoctorAppointmentsComponent implements OnInit {
  api = inject(ApiService);
  appointments = signal<Appointment[]>([]);
  loading = signal(true);
  editingNotes = signal<string | null>(null);
  notesText = '';

  ngOnInit() { this.load(); }

  load() {
    this.loading.set(true);
    this.api.getDoctorAppointments().subscribe({
      next: d => { this.appointments.set(d); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }

  get today() { return new Date().toISOString().split('T')[0]; }
  get todayApts() { return this.appointments().filter(a => a.date === this.today); }
  get pastApts()  { return this.appointments().filter(a => a.date < this.today); }
  get upcoming()  { return this.appointments().filter(a => a.date > this.today); }

  startEdit(apt: Appointment) { this.editingNotes.set(apt.id); this.notesText = apt.notes; }

  saveNotes(apt: Appointment) {
    this.api.updateAptNotes(apt.id, this.notesText).subscribe(() => {
      apt.notes = this.notesText;
      this.editingNotes.set(null);
    });
  }

  statusColor(s: string) {
    const m: any = { waiting: '#ff9800', in_progress: '#1565c0', completed: '#4caf50', cancelled: '#f44336', skipped: '#9e9e9e' };
    return m[s] || '#616161';
  }
}
