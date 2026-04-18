import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from '../../../core/services/auth.service';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-receptionist-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule, MatIconModule, MatButtonModule],
  templateUrl: './receptionist-layout.component.html',
  styleUrls: ['./receptionist-layout.component.scss']
})
export class ReceptionistLayoutComponent implements OnInit {
  auth        = inject(AuthService);
  api         = inject(ApiService);
  router      = inject(Router);
  sidebarOpen = signal(true);
  department  = signal<string>('');

  navItems = [
    { label: 'Dashboard',     icon: 'dashboard',   route: '/receptionist/dashboard' },
    { label: 'Book Walk-in',  icon: 'add_circle',  route: '/receptionist/book' },
    { label: 'Patients',      icon: 'people',      route: '/receptionist/patients' },
    { label: 'Queue',         icon: 'view_list',   route: '/receptionist/queue' },
    { label: 'Prescriptions', icon: 'description', route: '/receptionist/prescriptions' },
  ];

  ngOnInit() {
    this.api.getReceptionistMe().subscribe(data => {
      this.department.set(data.department?.name || '');
    });
  }

  toggleSidebar() { this.sidebarOpen.update(v => !v); }
  logout() { this.auth.logout(); }
}
