import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from '../../../core/services/auth.service';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-doctor-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, MatIconModule, MatButtonModule],
  templateUrl: './doctor-layout.component.html',
  styleUrls: ['./doctor-layout.component.scss']
})
export class DoctorLayoutComponent implements OnInit {
  auth = inject(AuthService);
  api  = inject(ApiService);
  sidebarOpen = signal(true);
  waitingCount = signal(0);

  navItems = [
    { label: 'Dashboard',   icon: 'dashboard', route: '/doctor/dashboard', badge: false },
    { label: 'My Queue',    icon: 'queue',     route: '/doctor/queue',     badge: true  },
    { label: 'My Patients', icon: 'people',    route: '/doctor/patients',  badge: false },
  ];

  ngOnInit() { this.loadQueue(); }

  toggleSidebar() { this.sidebarOpen.update(v => !v); }

  loadQueue() {
    this.api.getDoctorQueue().subscribe(q => this.waitingCount.set(q.waiting || 0));
  }
}
