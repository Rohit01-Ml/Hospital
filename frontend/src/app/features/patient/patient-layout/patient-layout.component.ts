import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MatBadgeModule } from '@angular/material/badge';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { AuthService } from '../../../core/services/auth.service';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-patient-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive,
    MatSidenavModule, MatToolbarModule, MatIconModule,
    MatButtonModule, MatListModule, MatMenuModule, MatBadgeModule],
  templateUrl: './patient-layout.component.html',
  styleUrls: ['./patient-layout.component.scss']
})
export class PatientLayoutComponent implements OnInit {
  auth = inject(AuthService);
  api  = inject(ApiService);
  sidenavOpen = signal(true);
  unreadCount = signal(0);

  navItems = [
    { label: 'Dashboard',          icon: 'dashboard',             route: '/patient/dashboard' },
    { label: 'Book Appointment',   icon: 'add_circle',            route: '/patient/book' },
    { label: 'My Appointments',    icon: 'calendar_today',        route: '/patient/appointments' },
    { label: 'Prescriptions',      icon: 'description',           route: '/patient/prescriptions' },
    { label: 'Lab Tests',          icon: 'biotech',               route: '/patient/lab-tests' },
    { label: 'Reports',            icon: 'assessment',            route: '/patient/reports' },
    { label: 'Medicine Reminders', icon: 'medication',            route: '/patient/medicine-reminders' },
    { label: 'Payments',           icon: 'payment',               route: '/patient/payments' },
    { label: 'Symptom Checker',    icon: 'psychology',            route: '/patient/symptom-checker' },
    { label: 'Notifications',      icon: 'notifications',         route: '/patient/notifications', badge: true },
  ];

  constructor() {
    inject(BreakpointObserver).observe([Breakpoints.Handset]).subscribe(r => {
      this.sidenavOpen.set(!r.matches);
    });
  }

  ngOnInit() { this.loadUnread(); }

  loadUnread() {
    this.api.getUnreadCount().subscribe(r => this.unreadCount.set(r.count));
  }
}
