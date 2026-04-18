import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { forkJoin } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';
import { Appointment, Prescription, MedicineReminder } from '../../../shared/models/models';
// forkJoin kept for parallel API calls

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, MatCardModule, MatButtonModule, MatIconModule, MatProgressSpinnerModule, MatChipsModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  api  = inject(ApiService);
  auth = inject(AuthService);

  loading = signal(true);
  appointments = signal<Appointment[]>([]);
  todayApts    = signal<Appointment[]>([]);
  prescriptions = signal<Prescription[]>([]);
  activeReminders = signal<MedicineReminder[]>([]);

  ngOnInit() {
    forkJoin({
      apts: this.api.getAppointments(),
      rx: this.api.getPrescriptions(),
      reminders: this.api.getActiveReminders(),
    }).subscribe({
      next: ({ apts, rx, reminders }) => {
        const today = new Date().toISOString().split('T')[0];
        this.appointments.set(apts);
        this.todayApts.set(apts.filter(a => a.date === today && a.status !== 'cancelled'));
        this.prescriptions.set(rx);
        this.activeReminders.set(reminders);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  get stats() {
    return [
      { label: "Today's Visits",   value: this.todayApts().length,       icon: 'today',       color: '#00897b', route: '/patient/appointments' },
      { label: 'Prescriptions',    value: this.prescriptions().length,    icon: 'description', color: '#7b1fa2', route: '/patient/prescriptions' },
      { label: 'Active Reminders', value: this.activeReminders().length,  icon: 'medication',  color: '#e53935', route: '/patient/medicine-reminders' },
    ];
  }

  statusClass(s: string) {
    return s.replace('_', '-');
  }
}
