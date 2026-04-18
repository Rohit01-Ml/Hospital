import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [
    CommonModule, RouterOutlet, RouterLink, RouterLinkActive,
    MatSidenavModule, MatToolbarModule, MatIconModule,
    MatButtonModule, MatListModule, MatMenuModule
  ],
  templateUrl: './admin-layout.component.html',
  styleUrls: ['./admin-layout.component.scss']
})
export class AdminLayoutComponent {
  auth = inject(AuthService);
  sidenavOpen = signal(true);

  navItems = [
    { label: 'Dashboard',       icon: 'dashboard',         route: '/admin/dashboard' },
    { label: 'Doctors',         icon: 'medical_services',  route: '/admin/doctors' },
    { label: 'Specializations', icon: 'category',          route: '/admin/specializations' },
    { label: 'Queue Control',   icon: 'queue',             route: '/admin/queue' },
    { label: 'Lab Tests',       icon: 'biotech',           route: '/admin/lab-tests' },
    { label: 'Reports',         icon: 'assessment',        route: '/admin/reports' },
    { label: 'Prescriptions',   icon: 'description',       route: '/admin/prescriptions' },
    { label: 'Hospitals',       icon: 'business',          route: '/admin/hospitals' },
    { label: 'Notifications',   icon: 'campaign',          route: '/admin/notifications' },
  ];

  constructor() {
    inject(BreakpointObserver).observe([Breakpoints.Handset]).subscribe(r => {
      this.sidenavOpen.set(!r.matches);
    });
  }
}
