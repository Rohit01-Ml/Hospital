import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { forkJoin } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { Appointment } from '../../../shared/models/models';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, MatIconModule, MatButtonModule, MatProgressSpinnerModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.scss']
})
export class AdminDashboardComponent implements OnInit {
  private api = inject(ApiService);
  loading = signal(true);

  totals = signal({ doctors: 0, specs: 0, appointments: 0, today: 0, waiting: 0, completed: 0, labTests: 0, reports: 0, revenue: 0 });
  todayApts = signal<Appointment[]>([]);

  ngOnInit() {
    const today = new Date().toISOString().split('T')[0];
    forkJoin({
      doctors: this.api.getDoctors(),
      specs:   this.api.getSpecializations(),
      apts:    this.api.getAppointments(),
      labBookings: this.api.getLabBookings(),
      reports: this.api.getReports(),
      payments: this.api.getPayments()
    }).subscribe({
      next: ({ doctors, specs, apts, labBookings, reports, payments }) => {
        const todayList = apts.filter(a => a.date === today);
        this.totals.set({
          doctors: doctors.length,
          specs:   specs.length,
          appointments: apts.length,
          today:   todayList.length,
          waiting:   apts.filter(a => a.status === 'waiting').length,
          completed: apts.filter(a => a.status === 'completed').length,
          labTests: labBookings.length,
          reports: reports.length,
          revenue: payments.filter((p: any) => p.status === 'paid').reduce((s: number, p: any) => s + p.amount, 0)
        });
        this.todayApts.set(todayList.slice(0, 8));
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  get stats() {
    const t = this.totals();
    return [
      { label: 'Total Doctors',      value: t.doctors,      icon: 'medical_services', color: '#3949ab', route: '/admin/doctors' },
      { label: 'Specializations',    value: t.specs,        icon: 'category',          color: '#8e24aa', route: '/admin/specializations' },
      { label: "Today's Patients",   value: t.today,        icon: 'today',             color: '#00897b', route: '/admin/queue' },
      { label: 'Waiting',            value: t.waiting,      icon: 'hourglass_empty',   color: '#f57c00', route: '/admin/queue' },
      { label: 'Lab Bookings',       value: t.labTests,     icon: 'biotech',           color: '#0097a7', route: '/admin/lab-tests' },
      { label: 'Reports',            value: t.reports,      icon: 'assessment',        color: '#7b1fa2', route: '/admin/reports' },
      { label: 'Completed Today',    value: t.completed,    icon: 'check_circle',      color: '#2e7d32', route: '/admin/queue' },
      { label: 'Revenue Collected',  value: `₹${t.revenue}`,icon: 'currency_rupee',   color: '#c62828', route: '/admin/dashboard' },
    ];
  }

  statusClass(s: string) { return s.replace('_', '-'); }
}
