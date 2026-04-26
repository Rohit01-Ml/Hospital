import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { forkJoin } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';
import { Appointment, DoctorQueueStatus } from '../../../shared/models/models';
// allApts removed — Total Appointments and Prescriptions stats removed per spec

@Component({
  selector: 'app-doctor-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, MatCardModule, MatButtonModule,
    MatIconModule, MatProgressSpinnerModule, MatChipsModule, MatDividerModule],
  templateUrl: './doctor-dashboard.component.html',
  styleUrls: ['./doctor-dashboard.component.scss']
})
export class DoctorDashboardComponent implements OnInit {
  api  = inject(ApiService);
  auth = inject(AuthService);
  loading   = signal(true);
  queue     = signal<DoctorQueueStatus | null>(null);
  todayApts = signal<Appointment[]>([]);
  doctorInfo = signal<any>(null);
  today = new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  ngOnInit() {
    forkJoin({
      me: this.api.getDoctorMe(),
      queue: this.api.getDoctorQueue(),
      today: this.api.getDoctorTodayAppointments(),
    }).subscribe({
      next: ({ me, queue, today }) => {
        this.doctorInfo.set(me);
        this.queue.set(queue);
        this.todayApts.set(today);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  get stats() {
    const q = this.queue();
    return [
      { label: "Today's Patients", value: q?.total_patients || 0, icon: 'people',          color: '#1565c0', route: '/doctor/queue' },
      { label: 'Waiting',          value: q?.waiting || 0,        icon: 'hourglass_empty', color: '#f57c00', route: '/doctor/queue' },
      { label: 'In Progress',      value: q?.in_progress || 0,   icon: 'medical_services', color: '#7b1fa2', route: '/doctor/queue' },
      { label: 'Completed Today',  value: q?.completed || 0,     icon: 'check_circle',     color: '#2e7d32', route: '/doctor/queue' },
    ];
  }

  timeOfDay() {
    const h = new Date().getHours();
    return h < 12 ? 'morning' : h < 17 ? 'afternoon' : 'evening';
  }

  get progressPct() {
    const q = this.queue();
    if (!q || !q.total_patients) return 0;
    return Math.round(((q.completed || 0) / q.total_patients) * 100);
  }

  statusColor(s: string) {
    const m: any = { waiting: '#ff9800', in_progress: '#1565c0', completed: '#4caf50', cancelled: '#f44336', skipped: '#9e9e9e' };
    return m[s] || '#616161';
  }
}
